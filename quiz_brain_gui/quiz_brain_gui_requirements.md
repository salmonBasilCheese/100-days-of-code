# システム要件定義書: Quizler App (Day 34: Quiz Brain GUI)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 画面およびウィンドウ仕様 (Window & Layout)
* **GUIフレームワーク**: Python標準 `tkinter`
* **ウィンドウ背景色**: `THEME_COLOR = "#375362"`
* **ウィンドウパディング**: `padx=20, pady=20`
* **ウィンドウタイトル**: `"Quizzler"`
* **レイアウト方式**: `grid()` (2列 × 3行構成)

### 1.2 ウィジェット構成と配置 (Grid Matrix)
1. **Score Label (行0, 列1)**:
   * 表示内容: `"Score: {score}"`
   * スタイル: 文字色 `"white"`, 背景色 `THEME_COLOR`, フォント `("Arial", 12, "bold")`
   * アライメント: 右寄せまたは通常配置
2. **Card Canvas (行1, 列0, columnspan=2)**:
   * 解像度: 幅 300px × 高さ 250px
   * 初期背景色: `"white"`, `highlightthickness=0`
   * パディング: `pady=50`
   * テキスト要素:
     * 配置座標: `(150, 125)` (中央)
     * 折り返し幅 (`width`): 280px (枠外はみ出し防止境界)
     * フォント: `("Arial", 18, "italic")`
     * 文字色: `THEME_COLOR`
3. **False Button (行2, 列1)**:
   * 画像ボタン: `images/false.png` (または直下 `false.png`)
   * スタイル: `highlightthickness=0`, `bd=0`, 背景色 `THEME_COLOR`, `activebackground=THEME_COLOR`
   * アクション: `false_pressed()` (回答 "False" を判定)
4. **True Button (行2, 列0)**:
   * 画像ボタン: `images/true.png` (または直下 `true.png`)
   * スタイル: `highlightthickness=0`, `bd=0`, 背景色 `THEME_COLOR`, `activebackground=THEME_COLOR`
   * アクション: `true_pressed()` (回答 "True" を判定)

### 1.3 外部データソース (External API)
* **API エンドポイント**: `https://opentdb.com/api.php?amount=10&type=boolean`
* **データ形式**: JSON (`results` 配下に `question`, `correct_answer` を内包)

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 回答フィードバック時の排他制御（連打・二重加算防止）
* 回答ボタン（True / False）押下時:
  * 正解時は Canvas 背景色を `"green"`、不正解時は `"red"` に変更する。
  * **ボタン無効化制約**: フィードバック表示中の 1000 ミリ秒（1秒）間、`true_button.config(state="disabled")` および `false_button.config(state="disabled")` を実行し、連打による多重スコア加算やインデックス超過を完全に遮断する。
  * 次問表示時に `state="normal"` へ復帰させ、Canvas 背景色を `"white"` に戻す。

### 2.2 リスト枯渇・終了境界 (End of Quiz)
* `quiz.still_has_questions()` が `False` に達した場合:
  * Canvas テキストを `"You've reached the end of the quiz."` に更新する。
  * スコアラベルを最終結果（例: `Score: {score}/{total}`）に確定させる。
  * True / False ボタンを恒久的に無効化（`state="disabled"`）し、`IndexError` を防止する。

### 2.3 文字列デコード境界 (HTML Entities)
* Open Trivia DB 由来の問題文に含まれる HTML 特殊記号（`&quot;`, `&#039;`, `&amp;` 等）は、Canvas 表示前に `html.unescape()` で確実に可読文字列にデコードする。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 クラス設計と責務の分離 (OOP Architecture)
1. **`Question` (`question_model.py`)**:
   * 単一問題のデータコンテナ (`self.text`, `self.answer`)。
2. **`QuizBrain` (`quiz_brain.py`)**:
   * 純粋なロジック層。CLI依存（`input()` / `print()`）を完全に排除。
   * `still_has_questions() -> bool`: 未出題問題の有無を返す。
   * `next_question() -> str`: 次の問題文を HTML デコードして返す。
   * `check_answer(user_answer: str) -> bool`: 正否を判定し、スコアを加算して真偽値を返す。
3. **`QuizInterface` (`ui.py`)**:
   * GUI プレゼンテーション層。
   * `QuizBrain` インスタンスを注入（DI）して保持。
   * ウィンドウ描画、Canvas / Label 更新、タイマー非同期フィードバック（`window.after(1000, ...)`）を統括。
4. **`main.py`**:
   * データロード、モデル変換、コントローラおよび UI の結合と起動。

### 3.2 状態遷移フロー

```
[START]
   |
   v
[GET_QUESTION: 次問表示] <---------------------------------------+
   ・Canvas背景: "white"                                        |
   ・Text: "Q.{num}: {decoded_question}"                        |
   ・Buttons: state="normal"                                    |
   |                                                            |
   +---> [ユーザー操作: True / False 押下]                       |
         ・Buttons: state="disabled" (連打防止ロック)            |
         ・is_correct = quiz.check_answer(...)                  |
         |                                                      |
         +---> (is_correct == True)  ---> Canvas背景: "green"    |
         +---> (is_correct == False) ---> Canvas背景: "red"      |
         ・Score Label 更新                                      |
         ・window.after(1000, get_next_question)                |
               |                                                |
               +---> (1秒後: still_has_questions == True) ------+
               |
               +---> (1秒後: still_has_questions == False)
                     ・Canvas背景: "white"
                     ・CanvasText: "You've reached the end of the quiz."
                     ・Buttons: state="disabled" (終了固定)
                     [FINISH]
```

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 アセット参照保護
* 画像ファイルパス（`images/true.png` または直下 `true.png`）を動的に探索・フォールバックし、実行パスの相違による起動失敗を防止する。

### 4.2 ネットワーク例外安全
* `data.py` での API 取得失敗（タイムアウト・オフライン）時、空リストを返して即座に終了ダイアログを出力し、未定義クラッシュを防ぐ。

---

## 5. モジュール構成 (Architecture)

```
quiz_brain_gui/
├── images/
│   ├── false.png        # 不正解ボタン画像
│   └── true.png         # 正解ボタン画像
├── data.py              # Open Trivia DB API通信
├── question_model.py    # Questionデータクラス
├── quiz_brain.py        # クイズロジック（CUI依存を完全排除）
├── ui.py                # Tkinter GUIインターフェース（QuizInterface）
├── main.py              # アプリケーションエントリーポイント
└── requirements.txt     # 依存ライブラリ (requests)
```
