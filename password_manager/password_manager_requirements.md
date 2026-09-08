# システム要件定義書: Password Manager (Day 29 / Day 30)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 画面およびウィンドウ仕様 (Window & Layout)
* **GUIフレームワーク**: Python標準 `tkinter` (`messagebox` 含む)
* **ウィンドウパディング**: `padx=50, pady=50`
* **ウィンドウタイトル**: `"Password Manager"`
* **レイアウト方式**: `grid()`（3列 × 5行構成）

### 1.2 ウィジェット構成と配置 (Grid Matrix)
1. **Canvas (行0, 列1)**:
   * サイズ: 幅 200px × 高さ 200px
   * 画像アセット: `logo.png` (中心 `(100, 100)`)
2. **Website**:
   * Label (行1, 列0): テキスト `"Website:"`
   * Entry (行1, 列1): `width=21` (検索ボタン併設のため縮小配置)
   * Search Button (行1, 列2): テキスト `"Search"`, `width=13`, アクション `search_website()`
3. **Email/Username**:
   * Label (行2, 列0): テキスト `"Email/Username:"`
   * Entry (行2, 列1, columnspan=2): `width=38`
   * 初期値: 事前に指定されたデフォルトメールアドレス（例: `"user@example.com"`）を自動入力
4. **Password**:
   * Label (行3, 列0): テキスト `"Password:"`
   * Entry (行3, 列1): `width=21`
   * Generate Button (行3, 列2): テキスト `"Generate Password"`, `width=13`, アクション `generate_password()`
5. **Add Button (行4, 列1, columnspan=2)**:
   * テキスト: `"Add"`, `width=36`, アクション `save_password()`

### 1.3 外部インターフェース (Clipboard & Files)
* **クリップボード連携**: `pyperclip.copy()` を使用し、パスワード生成時に自動でクリップボードへ格納。
* **データ永続化ファイル**: `data.json`

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 必須フィールドの検証制約
* `Website` または `Password` の文字列長が 0（空文字）の場合:
  * データの保存処理を即座に中断する。
  * 警告ダイアログ `messagebox.showwarning(title="Oops", message="Please make sure you haven't left any fields empty!")` を表示。

### 2.2 データ永続化の例外境界 (JSON Handling)
* `data.json` の読み書きにおいて、以下の境界状態を安全にハンドリングする:
  1. **初回起動時（ファイル未存在）**: `FileNotFoundError` を捕捉し、新規辞書を作成して `"w"` モードで保存。
  2. **ファイル空・破損時**: `json.JSONDecodeError` を捕捉し、空辞書として初期化して上書き修復。
  3. **正常追記時**: 既存辞書を読み込み（`json.load()`）、新データをマージ（`update()`）した上で `"w"` モードでインデント整形成形（`indent=4`）して書き込む。

### 2.3 検索機能の境界処理 (Search Invariant)
* `Search` ボタン押下時:
  * Website エントリーが空の場合は処理中断。
  * `data.json` が存在しない場合は「データファイルが存在しません」と通知。
  * 該当 Website が辞書に存在する場合:
    * `messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")` を表示。
  * 該当 Website が存在しない場合:
    * `messagebox.showinfo(title="Error", message=f"No details for {website} exists.")` を表示。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 データ構造 (JSON Schema)
Website名をルートキーとするネストされた辞書構造として永続化する。
```json
{
  "WebsiteName": {
    "email": "user@example.com",
    "password": "GeneratedSecurePassword123!"
  }
}
```

### 3.2 パスワード生成アルゴリズム (`generate_password`)
* 文字種リスト:
  * Letters: `a-z`, `A-Z` (8〜10文字をランダム抽出)
  * Numbers: `0-9` (2〜4文字をランダム抽出)
  * Symbols: `!`, `#`, `$`, `%`, `&`, `(`, `)`, `*`, `+` (2〜4文字をランダム抽出)
* 内包表記と乱数によるリスト結合後、`random.shuffle()` で順序を撹乱。
* 生成文字列を `password_entry` に自動挿入（既存文字があれば消去後に挿入）。
* `pyperclip.copy(password)` を呼び出し、即座にペースト可能な状態にする。

### 3.3 保存フロー (`save_password`)
1. 入力値の取得（`get()`）および空文字バリデーション。
2. 新規データ辞書オブジェクトの構築: `{website: {"email": email, "password": password}}`。
3. `try-except-else` 構文によるファイル更新:
   ```python
   try:
       with open("data.json", "r", encoding="utf-8") as file:
           data = json.load(file)
   except (FileNotFoundError, json.JSONDecodeError):
       data = {}
   
   data.update(new_data)
   
   with open("data.json", "w", encoding="utf-8") as file:
       json.dump(data, file, indent=4, ensure_ascii=False)
   ```
4. 入力フィールドの初期化: `website_entry` と `password_entry` をクリアし、カーソルを `website_entry` にフォーカス（`focus()`）。

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 アセット依存性と例外安全
* `logo.png` がカレントディレクトリに存在しない場合でもプログラムがクラッシュしないよう、存在チェックを行い、不在時はプレースホルダー（四角形等）を描画して起動を継続する。

### 4.2 クリップボードライブラリのフォールバック
* `pyperclip` が環境に未インストール、またはOS固有のクリップボードデーモン不在（Linux等）でエラーを送出する場合、例外をキャッチして警告を表示し、パスワードのエントリーへの入力・保存自体は正常に完了させる。

---

## 5. モジュール構成 (Architecture)

```
password_manager/
├── logo.png          # ロゴ画像 (200x200)
├── data.json         # (自動生成) アカウント・パスワード情報データベース
├── main.py           # Tkinter UI、生成・保存・検索ロジック統括
└── requirements.txt  # 依存外部ライブラリ (pyperclip)
```
