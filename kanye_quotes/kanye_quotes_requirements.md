# システム要件定義書: Kanye Quotes App (Day 33)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 画面およびウィンドウ仕様 (Window & Layout)
* **GUIフレームワーク**: Python標準 `tkinter`
* **ウィンドウタイトル**: `"Kanye Says..."`
* **ウィンドウパディング**: `padx=50, pady=50`
* **レイアウト方式**: `grid()` (1列 × 2行構成)

### 1.2 ウィジェット構成と配置 (Grid Matrix)
1. **Canvas (行0, 列0)**:
   * 解像度: 幅 300px × 高さ 414px
   * 背景画像: `background.png` (中心 `(150, 207)`)
   * テキスト要素:
     * 座標: `(150, 207)`
     * 折り返し幅 (`width`): 250px (吹き出し枠内に収めるための境界制約)
     * フォント: `("Arial", 25, "bold")` (長文時の可読性を担保する標準相場)
     * 文字色: `"white"`
2. **Kanye Button (行1, 列0)**:
   * 画像ボタン: `kanye.png`
   * スタイル: `highlightthickness=0`, `bd=0`
   * アクション: `get_quote()` (API経由で名言を取得しCanvasテキストを更新)

### 1.3 外部インターフェース (External API)
* **エンドポイント**: `https://api.kanye.rest`
* **HTTPメソッド**: `GET`
* **通信ライブラリ**: `requests`
* **レスポンス仕様**: JSON形式
  ```json
  {
    "quote": "string"
  }
  ```

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 ネットワーク通信例外とタイムアウト防御
* **タイムアウト設定**: `requests.get(..., timeout=5)` を明示指定。サーバー無応答によるメインスレッド（GUI）の永久フリーズを防止する。
* **HTTPステータス例外**: `response.raise_for_status()` を実行し、4xx/5xx系エラーを捕捉する。
* **ネットワーク切断防御**: `requests.exceptions.RequestException` を `try-except` で捕捉し、UI上に `"Failed to connect to API."` などの安全なメッセージを描画してクラッシュを防止する。

### 2.2 テキスト長スケーリング境界 (Wrap & Font Size)
* APIから返却される名言の長さに応じ、Canvas外へのはみ出しを防止する:
  * 100文字超: フォントサイズを `18pt` に自動縮小
  * 100文字以下: 標準の `24pt` で描画

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 状態遷移フロー

```
[INIT: ウィンドウ初期化]
   |
   +---> [get_quote() 初回即時実行]
   |           |
   |           v
   |     [GET https://api.kanye.rest]
   |           |
   |           +---> (成功: 200 OK) ---> [Canvasテキストを最新の名言に更新]
   |           |
   |           +---> (通信失敗 / タイムアウト) ---> [エラーメッセージをCanvasに表示]
   |
[IDLE: 待機状態] <---------------------------------------------+
   |                                                            |
   +---> (ユーザー操作: kanye_button 押下)                      |
         ・get_quote() 実行 ------------------------------------+
```

### 3.2 初期ロード仕様
* 起動直後、ダミー文字列（`"Kanye Quote Goes HERE"`）を表示させたままにせず、`mainloop()` 直前に `get_quote()` を1回自動呼び出しして最新の名言を表示した状態でアプリを立ち上げる。

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 アセットの安全参照
* `background.png`, `kanye.png` の存在を確認し、ファイルパス不備による `TclError` を防ぐ。

### 4.2 依存管理
* `requests` パッケージを `requirements.txt` に定義。

---

## 5. モジュール構成 (Architecture)

```
kanye_quotes/
├── background.png   # 吹き出し背景画像 (300x414)
├── kanye.png        # カニエの顔ボタン画像
├── main.py          # Tkinter GUIおよびREST API通信統括
└── requirements.txt # 依存ライブラリ (requests)
```
