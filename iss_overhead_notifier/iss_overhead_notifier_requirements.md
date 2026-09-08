# システム要件定義書: ISS Overhead Notifier (Day 33)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 実行主体およびインターフェース
* **実行環境**:
  * ローカル CLI (常駐ポーリング / 手動実行)
  * クラウド自動実行 (GitHub Actions 連携対応)
* **プロトコル**:
  * REST API (HTTPS GET)
  * SMTP over TLS (RFC 3207: Gmail `smtp.gmail.com:587`)

### 1.2 外部データソース (External APIs)
1. **ISS リアルタイム位置情報 API**:
   * エンドポイント: `http://api.open-notify.org/iss-now.json`
   * HTTPメソッド: `GET`
   * レスポンス仕様:
     ```json
     {
       "iss_position": {
         "latitude": "string (float)",
         "longitude": "string (float)"
       },
       "message": "success",
       "timestamp": 1234567890
     }
     ```
2. **日の出・日の入り時刻 API**:
   * エンドポイント: `https://api.sunrise-sunset.org/json`
   * パラメータ: `lat`, `lng`, `formatted=0`
   * レスポンス仕様:
     ```json
     {
       "results": {
         "sunrise": "2026-09-08T20:45:00+00:00",
         "sunset": "2026-09-09T09:15:00+00:00"
       },
       "status": "OK"
     }
     ```

### 1.3 観測基準座標と認証情報 (Configuration)
* **観測者位置（環境変数またはデフォルト値）**:
  * `MY_LAT`: 緯度 (float, 例: 東京 `35.6895` / ロンドン `51.507351`)
  * `MY_LONG`: 経度 (float, 例: 東京 `139.6917` / ロンドン `-0.127758`)
* **認証・通知先（環境変数）**:
  * `MY_EMAIL`: 送信元 Gmail アドレス
  * `MY_PASSWORD`: Google アプリパスワード (16桁)
  * `TO_EMAIL`: 通知先メールアドレス (未設定時は `MY_EMAIL` へ送信)

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 接近判定境界 (Proximity Margin)
* **許容誤差**: 観測地点から **±5度以内**
  * 判定式:
    $$\|MY\_LAT - iss\_lat\| \le 5 \quad 	ext{and} \quad \|MY\_LONG - iss\_long\| \le 5$$

### 2.2 夜間（暗闇）判定境界 (Night Time Boundary)
* **タイムゾーン整合性**:
  * API の日の出・日の入り時刻は **UTC** であるため、現在時刻も厳格に **UTC** (`datetime.now(timezone.utc)`) を基準とする。
* **日付変更線を跨ぐ夜間判定**:
  * 日没後、または日の出前を「夜」と判定する論理和（OR）条件:
    $$	ext{now\_hour} \ge 	ext{sunset\_hour} \quad 	ext{or} \quad 	ext{now\_hour} \le 	ext{sunrise\_hour}$$

### 2.3 ネットワーク例外とタイムアウト境界
* 外部 API 通信には `timeout=10` を設定し、無応答によるプロセスの永久ハングを防止。
* 接近・夜間の両条件を満たさない場合は、**SMTP セッションを確立せずに早期リターン**（無駄なリソース消費と外部アクセスの防止）。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 処理シーケンス (Workflow)

```
[START]
   |
   +---> [GET iss-now.json] (timeout=10)
   |           |
   |           +---> (iss_latitude, iss_longitude を float 変換)
   |           v
   +---> [接近判定: abs(Δlat) <= 5 and abs(Δlong) <= 5]
   |           |
   |           +---> (NO: 範囲外) ---> [LOG: ISS is too far] ---> [SKIP / SLEEP]
   |           |
   |           v (YES: 接近中)
   +---> [GET sunrise-sunset.org] (timeout=10)
   |           |
   |           +---> (sunrise, sunset の UTC 時刻を取得)
   |           v
   +---> [夜間判定: now_utc >= sunset or now_utc <= sunrise]
   |           |
   |           +---> (NO: 昼間) ---> [LOG: Not dark enough] ---> [SKIP / SLEEP]
   |           |
   |           v (YES: 夜間かつ接近)
   +---> [SMTP 送信処理]
   |     ・smtp.gmail.com:587 (STARTTLS)
   |     ・Subject: "Look Up! 👆 (ISS is overhead)"
   |     ・Body: 観測座標、ISS現在座標、日照情報を記載
   |
   v
[FINISH / NEXT LOOP]
```

### 3.2 実行モード仕様
1. **シングル実行モード (`--once`)**:
   * 1回判定して終了（GitHub Actions 等の Cron 実行向け）。
2. **常駐ポーリングモード (デフォルト)**:
   * `while True` ループ内で 60 秒（`time.sleep(60)`）間隔で定期監視。

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 通信耐障害性
* API 呼び出し時の `requests.exceptions.RequestException` を個別にキャッチし、一時的なネットワーク断でデーモンが異常終了しないようログ出力後に待機・再試行する。

### 4.2 機密情報の保護
* メールアドレスやパスワードは環境変数から取得し、平文でのリポジトリコミットを禁止する。

---

## 5. モジュール構成 (Architecture)

```
iss_overhead_notifier/
├── main.py              # ISS座標追跡、日照時間計算、SMTP通知統括
└── requirements.txt     # 依存ライブラリ (requests)
```
