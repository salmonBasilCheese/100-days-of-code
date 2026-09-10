# システム要件定義書: Flight Deal Finder (Day 39-40: SerpAPI & Sheety Integration)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 実行主体およびインターフェース
* **実行環境**:
  * ローカル CLI (手動検証 / デバッグ)
  * クラウド自動実行 (GitHub Actions Cron / 毎日 JST 08:00 定期実行)
* **プロトコル**:
  * REST API (HTTPS GET / PUT) - Google スプレッドシート連携 (Sheety API)
  * REST API (HTTPS GET) - Google Flights 検索 (SerpAPI)
  * Webhook (HTTPS POST) - 最安値ディール通知 (Discord Webhook)

### 1.2 外部データソース / 連携サービス
1. **Sheety API (Google Sheets DB)**:
   * 役割: 目的地リスト、IATA 空港コード、基準最低価格（閾値）のストレージ
   * エンドポイント: `https://api.sheety.co/<SHEETY_USERNAME>/<PROJECT_NAME>/<SHEET_NAME>`
   * 認証方式: Bearer Token (`Authorization: Bearer <SHEETY_TOKEN>`)
   * データ構造（行単位）:
     * `city`: 都市名 (例: Paris)
     * `iataCode`: 空港コード (例: CDG)
     * `lowestPrice`: 目標許容価格 (JPY, 数値)
2. **SerpAPI (Google Flights Engine)**:
   * 役割: Google Flights のリアルタイム最安値便スクレイピング・検索
   * エンドポイント: `https://serpapi.com/search`
   * 主要パラメータ:
     * `engine`: `google_flights`
     * `departure_id`: 出発地 IATA コード (デフォルト: `TYO` / 東京全域)
     * `arrival_id`: 目的地 IATA コード (例: `CDG`)
     * `outbound_date`: 往路出発日 (`YYYY-MM-DD`)
     * `return_date`: 復路帰国日 (`YYYY-MM-DD`)
     * `currency`: `JPY`
     * `hl`: `en`
     * `api_key`: `SERP_API_KEY`
3. **Discord Webhook (通知先)**:
   * 役割: 最安値ディール検出時の即時プッシュ通知
   * 認証・宛先: `DISCORD_WEBHOOK_URL`

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 クォータ防衛境界 (Quota Conservation Invariant)
* **SerpAPI 無料枠**: 月 100 リクエスト。
  * スプレッドシート内の目的都市数は **最大 3〜4 都市** に制限する。
  * ローカル開発環境では `requests_cache`（キャッシュ有効期限 12〜24 時間）を必須適用し、同一パラメータの重複消費を防止する。
* **Sheety API 無料枠**: 月 200 リクエスト。
  * 毎日のバッチ実行回数は 1 回（1日あたり最大 1 回の全行取得）。

### 2.2 検索期間・滞在期間の相場仕様
* **往路出発範囲**: 明日（`today + 1 day`）から **6 か月後（`today + 180 days`）** の期間。
* **滞在期間 (Stay Duration)**: **7 日間〜14 日間**（往復航空券の標準相場として初期値 7 日を適用）。

### 2.3 最安値判定および早期リターン境界
* 判定式:
  $$	ext{current\_price} < 	ext{sheet\_lowest\_price}$$
* 境界処理:
  * 市場価格がシートの目標値以上（$	ext{current\_price} \ge 	ext{sheet\_lowest\_price}$）の場合、Discord Webhook は送信しない。
  * 該当する便が存在しない、または価格が取得できなかった（`None`）場合は例外で落とさず警告ログを出力して次都市へスキップする。

### 2.4 通信耐性とタイムアウト
* すべての外部リクエスト（Sheety, SerpAPI, Discord）に `timeout=15` を設定。
* 通貨単位は `JPY` に固定し、為替や地域差による価格判定の狂いを排除する。

---

## 3. 操作・ロジック仕様 (Data Flow & State Machine)

```
[START]
   |
   +---> [環境変数バリデーション] (SHEETY_TOKEN, SERP_API_KEY, DISCORD_WEBHOOK_URL)
   |           |
   |           +---> (欠落あり) ---> [FATAL: 終了]
   |           v
   +---> [DataManager: Sheety から目的地一覧を取得]
   |           |
   |           +---> (空または不正データ除外)
   |           v
   +---> [ループ: 各目的地ごと]
   |           |
   |           +---> [FlightSearch: SerpAPI で最安値便を検索] (キャッシュ適用)
   |           |           |
   |           |           +---> (フライトなし/取得失敗) ---> [WARN: スキップ]
   |           |           v
   |           +---> [FlightData: 価格・日程・便情報を構造化]
   |           |           |
   |           |           v
   |           +---> [価格比較: current_price < sheet_lowestPrice]
   |                       |
   |                       +---> (条件不成立) ---> [LOG: 最安値更新なし]
   |                       v (ディール成立)
   |                 [NotificationManager: Discord Webhook 配信]
   |
   v
[SUCCESS: 全都市走査完了] ---> [END]
```

---

## 4. モジュール構成・責務分離 (Architecture)

```
flight_deal_finder/
├── .env.example                  # 環境変数テンプレート
├── requirements.txt              # 依存関係 (requests, requests-cache, python-dotenv)
├── data_manager.py               # DataManager クラス (Sheety API 通信担当)
├── flight_search.py              # FlightSearch クラス (SerpAPI 通信・キャッシュ担当)
├── flight_data.py                # FlightData クラス (航空券情報データモデル)
├── notification_manager.py       # NotificationManager クラス (Discord Webhook 配信)
├── main.py                       # メインオーケストレーター (統合処理)
└── flight_deal_requirements.md   # 本要件定義書
```
