# システム要件定義書: Rain Alert Notifier (Day 35: API Key, Auth & Webhook/Telegram)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 実行主体およびインターフェース
* **実行環境**:
  * ローカル CLI (手動実行 / 単体テスト)
  * クラウド自動実行 (GitHub Actions Cron / JST 06:00 定期実行)
* **プロトコル**:
  * REST API (HTTPS GET) - 天気予報データ取得
  * Webhook / REST API (HTTPS POST) - プッシュ通知送信

### 1.2 外部データソース (Weather API)
* **プロバイダ**: OpenWeatherMap API (5 Day / 3 Hour Forecast API または One Call API)
  * 標準推奨: `https://api.openweathermap.org/data/2.5/forecast` (無料枠で即時利用可能)
* **リクエストパラメータ**:
  * `lat`: 観測地点の緯度
  * `lon`: 観測地点の経度
  * `appid`: OpenWeatherMap API Key
  * `cnt`: `4` (直近12時間分: 3時間 × 4スライス)
* **レスポンス構造**:
  ```json
  {
    "list": [
      {
        "dt": 1725840000,
        "weather": [
          {
            "id": 500,
            "main": "Rain",
            "description": "light rain"
          }
        ]
      }
    ]
  }
  ```

### 1.3 通知インターフェース (Notification Channels - Discord & Telegram)
Twilio SMS の代替として、以下のいずれかまたは両方を環境変数に応じて動的ルーティングする:

1. **Discord Webhook**:
   * メソッド: `POST`
   * エンドポイント: `DISCORD_WEBHOOK_URL`
   * ペイロード:
     ```json
     {
       "content": "🌧️ **雨天通知**: 今日は雨が降る予報です。傘を持って出かけてください！"
     }
     ```
2. **Telegram Bot API**:
   * メソッド: `POST`
   * エンドポイント: `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage`
   * ペイロード:
     ```json
     {
       "chat_id": "<TELEGRAM_CHAT_ID>",
       "text": "🌧️ 雨天通知: 今日は雨が降る予報です。傘を持って出かけてください！"
     }
     ```

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 降水判定境界 (Weather Condition Invariants)
* **対象時間枠**: 今後 12 時間（直近 4 スライス分）。
* **降水判定コード**:
  * OpenWeatherMap の気象コード仕様:
    * `2xx`: Thunderstorm（雷雨）
    * `3xx`: Drizzle（霧雨）
    * `5xx`: Rain（雨）
    * `6xx`: Snow（雪）
  * 判定式:
    $$\exists \, item \in forecast[:4] \quad 	ext{s.t.} \quad condition\_id < 700$$

### 2.2 早期リターン境界 (Zero Unnecessary Requests)
* 直近 12 時間のすべての気象コードが `id >= 700`（晴れ、曇り、大気現象等）の場合:
  * 外部通知 Webhook / API の呼び出しを完全に遮断する。
  * ログに `No rain forecast in the next 12 hours. Notification skipped.` と出力して正常終了する。

### 2.3 通信例外とタイムアウト防御
* 天気 API および通知 Webhook / API の双方に `timeout=10` を設定。
* `requests.exceptions.RequestException`（オフライン、DNS解決不能、4xx/5xx系エラー）を捕捉し、スタックトレースではなく適切なエラーメッセージを標準エラー出力へ送出する。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 処理シーケンス (Workflow)

```
[START]
   |
   +---> [環境変数バリデーション]
   |           |
   |           +---> (必須変数欠落: OWM_API_KEY等) ---> [FATAL: 終了]
   |           v
   +---> [GET OpenWeatherMap Forecast] (cnt=4, timeout=10)
   |           |
   |           +---> (HTTP 200 OK)
   |           v
   +---> [降水判定ループ] (weather_id < 700)
   |           |
   |           +---> (全スライス >= 700) ---> [LOG: 傘不要] ---> [END]
   |           |
   |           v (降水を検知)
   +---> [通知メッセージ生成]
   |           |
   |           +---> DISCORD_WEBHOOK_URL が存在する場合 ---> [POST Discord]
   |           +---> TELEGRAM_BOT_TOKEN & CHAT_ID が存在する場合 ---> [POST Telegram]
   |           |
   v
[SUCCESS: 通知完了] ---> [END]
```

### 3.2 構成設計 (Configuration Invariants)
* 機密情報はコードに一切直書きせず、`os.environ` 経由で取得する。
* ローカル開発時は `.env`（`python-dotenv`）またはシェル環境変数をサポートし、リポジトリへのコミットを `.gitignore` で禁止する。

---

## 4. モジュール構成 (Architecture)

```
rain_alert/
├── .env.example         # 環境変数テンプレート（機密情報は含めない）
├── main.py              # 天気データ取得、降雨判定、Discord/Telegram通知統括
└── requirements.txt     # 依存ライブラリ (requests, python-dotenv)
```
