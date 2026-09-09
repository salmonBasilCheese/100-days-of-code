# システム要件定義書: Stock Trading News Alert (Day 36: NVDA Volatility & News Dispatcher)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 実行主体およびインターフェース
* **実行環境**:
  * ローカル CLI (手動実行 / 単体テスト)
  * クラウド自動実行 (GitHub Actions Cron / JST 06:30 米国市場クローズ後 定期実行)
* **プロトコル**:
  * REST API (HTTPS GET) - 株価時系列データ取得 (Alpha Vantage)
  * REST API (HTTPS GET) - 企業関連ニュース記事取得 (NewsAPI)
  * Webhook (HTTPS POST) - アラート通知送信 (Discord Webhook)

### 1.2 外部データソース (Financial & News APIs)
1. **Alpha Vantage API (株価データ)**:
   * エンドポイント: `https://www.alphavantage.co/query`
   * パラメータ:
     * `function`: `TIME_SERIES_DAILY`
     * `symbol`: `NVDA`
     * `apikey`: `ALPHA_VANTAGE_API_KEY`
     * `outputsize`: `compact` (直近100日分)
   * 取得対象:
     * `Time Series (Daily)` キー配下の最新確定取引日 ($D_0$) の終値 (`4. close`)
     * その直前の確定取引日 ($D_1$) の終値 (`4. close`)
2. **NewsAPI (ニュース記事データ)**:
   * エンドポイント: `https://newsapi.org/v2/everything`
   * パラメータ:
     * `q`: `NVIDIA`
     * `sortBy`: `publishedAt`
     * `language`: `en`
     * `pageSize`: `3`
     * `apiKey`: `NEWS_API_KEY`
   * 取得対象: `articles` 配列の先頭 3 件 (`articles[:3]`)

### 1.3 通知インターフェース (Discord Webhook)
* **エンドポイント**: `DISCORD_WEBHOOK_URL`
* **メソッド**: `POST`
* **メッセージフォーマット**:
  ```text
  NVDA: 🔺 5.20%
  Headline: NVIDIA Unveils Next-Gen AI Infrastructure Architecture
  Brief: NVIDIA announced a new suite of AI chips designed to improve inference speed...
  URL: https://example.com/article
  ```
  *(注: 下落時は `🔻`)*

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 変動率判定境界 (Volatility Threshold Invariant)
* **判定式**:
  $$\Delta = 	ext{close}_{D_0} - 	ext{close}_{D_1}$$
  $$	ext{diff\_percent} = rac{|\Delta|}{	ext{close}_{D_1}} 	imes 100$$
* **発火条件**:
  $$	ext{diff\_percent} \ge 5.0\%$$
* **シンボル判定**:
  * $\Delta \ge 0 \implies 	ext{🔺}$
  * $\Delta < 0 \implies 	ext{🔻}$

### 2.2 早期リターン境界 (Zero Unnecessary Requests)
* 変動率が閾値未満（$	ext{diff\_percent} < 5.0\%$）の場合:
  * NewsAPI へのリクエストを一切送信しない。
  * Discord Webhook へのリクエストを一切送信しない。
  * `[Skip] NVDA change (X.XX%) is below the 5.0% threshold.` を出力して即座に終了する。

### 2.3 休場日・週末データ欠落耐性 (Market Holiday Handling)
* `datetime.now() - timedelta(days=1)` のようなカレンダー日付ハードコードは禁止。
* `Time Series (Daily)` 内のキー（日付文字列）を降順ソートし、スライシング `[:2]` で直近2営業日を抽出する。

### 2.4 APIクォータ・レート制限の防御
* Alpha Vantage: 無料枠は 25 回/日（5 回/分）。
  * レスポンス内に `Note` や `Information` フィールドが存在する場合、レート制限到達例外として検出し標準エラー出力へ送出。
* 全外部通信に `timeout=10` を適用。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

```
[START]
   |
   +---> [環境変数バリデーション]
   |           |
   |           +---> (必須変数欠落: ALPHA_VANTAGE_API_KEY等) ---> [FATAL: 終了]
   |           v
   +---> [GET Alpha Vantage TIME_SERIES_DAILY] (timeout=10)
   |           |
   |           +---> (降順ソートで直近2営業日の終値抽出)
   |           v
   +---> [変動率計算] (diff_percent)
   |           |
   |           +---> (diff_percent < 5.0%) ---> [LOG: スキップ] ---> [END]
   |           |
   |           v (diff_percent >= 5.0%)
   +---> [GET NewsAPI NVIDIA ニュース] (limit=3, timeout=10)
   |           |
   |           v
   +---> [POST Discord Webhook] (最大3件のアラート送信)
   |           |
   v
[SUCCESS: 配信完了] ---> [END]
```

---

## 4. モジュール構成 (Architecture)

```
stock_news_alert/
├── .env.example              # 設定テンプレート
├── main.py                   # 株価判定・ニュース取得・Discord通知統括
├── requirements.txt          # 依存関係 (requests, python-dotenv)
└── stock_news_requirements.md # 本要件定義書
```
