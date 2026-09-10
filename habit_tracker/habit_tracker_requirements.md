# システム要件定義書: Habit Tracking Automation (Day 37: Pixela API Integration)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 実行主体およびインターフェース
* **実行環境**:
  * ローカル CLI (手動実行 / 単体テスト)
  * クラウド自動実行 (GitHub Actions Cron / 毎日 JST 23:00 打刻)
* **プロトコル**:
  * REST API (HTTPS POST / PUT / DELETE) - Pixela サービス連携

### 1.2 外部データソース / 連携先 (Pixela API)
* **ベースURL**: `https://pixe.la/v1/users`
* **認証方式**:
  * カスタムリクエストヘッダー: `X-USER-TOKEN: <PIXELA_TOKEN>`
* **エンドポイント一覧**:
  1. ユーザー作成 (初期セットアップ): `POST /v1/users`
  2. グラフ作成 (初期セットアップ): `POST /v1/users/<USERNAME>/graphs`
  3. ピクセル新規登録 (日常打刻): `POST /v1/users/<USERNAME>/graphs/<GRAPH_ID>`
  4. ピクセル更新 (データ修正): `PUT /v1/users/<USERNAME>/graphs/<GRAPH_ID>/<DATE>`
  5. ピクセル削除 (データ取消): `DELETE /v1/users/<USERNAME>/graphs/<GRAPH_ID>/<DATE>`

### 1.3 パラメータ仕様・命名制約
* **USERNAME**: `[a-z0-9-]{2,33}` (小文字英数・ハイフンのみ)
* **GRAPH_ID**: `[a-z0-9-]{1,17}` (小文字英数・ハイフンのみ)
* **TOKEN**: `[ -~]{8,128}` (API認証用シークレットキー)
* **DATE**: `yyyyMMdd` (8桁固定、例: `20260910`)
* **QUANTITY**: 文字列型 (例: `"1.5"`、グラフ定義が float の場合)
* **TIMEZONE**: `"Asia/Tokyo"` (日付ずれ防止)

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 ライフサイクル分離 (Lifecycle Segregation Invariant)
* **セットアップ操作 (一回限り)**:
  * ユーザー作成、グラフ作成は運用スクリプト本体の実行フローから分離する。
* **運用操作 (日常バッチ)**:
  * 日常の定期実行スクリプト (`main.py`) は「ピクセルの打刻・更新」に特化させ、余計なリクエストを送信しない。

### 2.2 Pixela 確率的リトライ制限耐性 (Retry Policy)
* Pixela は仕様上、無料利用枠等で間欠的に `503` または `{"isSuccess": false, "message": "Please retry..."}` を返却する場合がある。
* **対策**:
  * リクエスト失敗時、最大 4 回まで待機（指数バックオフ: 1秒, 2秒, 4秒）を挟んで自動再試行する。

### 2.3 タイムアウトと通信保護
* 全ての HTTP リクエストに `timeout=10` を適用し、プロセスハングを防御する。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

```
[START]
   |
   +---> [環境変数バリデーション]
   |           |
   |           +---> (必須変数欠落: PIXELA_TOKEN等) ---> [FATAL: 終了]
   |           v
   +---> [日付・打刻値の準備] (現在日付 yyyyMMdd, quantity)
   |           |
   |           v
   +---> [POST ピクセル登録] (X-USER-TOKEN ヘッダー付与)
   |           |
   |           +---> (isSuccess: true) ---> [SUCCESS: 打刻完了] ---> [END]
   |           |
   |           v (isSuccess: false または HTTP 503)
   +---> [リトライ試行] (最大 4 回バックオフ)
               |
               +---> (全試行失敗) ---> [FATAL: 終了]
```

---

## 4. モジュール構成 (Architecture)

```
habit_tracker/
├── .env.example                # 設定テンプレート
├── setup_graph.py              # 初回用: ユーザー登録・グラフ定義スクリプト
├── main.py                     # 運用時: 日常ピクセル打刻・自動化スクリプト
├── requirements.txt            # 依存関係 (requests, python-dotenv)
└── habit_tracker_requirements.md # 本要件定義書
```
