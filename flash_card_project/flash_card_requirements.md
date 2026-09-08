# システム要件定義書: Flash Card App (Day 31)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 画面およびウィンドウ仕様 (Window & Layout)
* **GUIフレームワーク**: Python標準 `tkinter`
* **ウィンドウ背景色**: `BACKGROUND_COLOR = "#B1DDC6"`
* **ウィンドウパディング**: `padx=50, pady=50`
* **ウィンドウタイトル**: `"Flashy"`
* **レイアウト方式**: `grid()`（2列 × 2行構成）

### 1.2 ウィジェット構成と配置 (Grid Matrix)
1. **Canvas (行0, 列0, columnspan=2)**:
   * 解像度: 幅 800px × 高さ 526px
   * 背景色: `BACKGROUND_COLOR`, `highlightthickness=0`
   * カード画像要素 (中心 `(400, 263)`):
     * 表面: `card_front.png`
     * 裏面: `card_back.png`
   * テキスト要素:
     * 言語タイトル: 座標 `(400, 150)`, フォント `("Arial", 40, "italic")`
       * 表面: `"French"`, 文字色 `"black"`
       * 裏面: `"English"`, 文字色 `"white"`
     * 単語テキスト: 座標 `(400, 263)`, フォント `("Arial", 60, "bold")`
       * 表面: フランス語単語, 文字色 `"black"`
       * 裏面: 英語対訳, 文字色 `"white"`
2. **Wrong Button (行1, 列0)**:
   * 画像ボタン: `wrong.png`
   * スタイル: `highlightthickness=0`, `bd=0`, 背景 `BACKGROUND_COLOR`
   * アクション: `next_card()`（現在の単語をリストに残したまま次へ）
3. **Right Button (行1, 列1)**:
   * 画像ボタン: `right.png`
   * スタイル: `highlightthickness=0`, `bd=0`, 背景 `BACKGROUND_COLOR`
   * アクション: `is_known()`（現在の単語をリストから削除・保存して次へ）

### 1.3 外部データソース (Data Source & Persistence)
* **マスターデータ**: `data/french_words.csv`（または直下の `french_words.csv`）
  * スキーマ: `French,English`（UTF-8エンコーディング）
* **学習進捗ファイル**: `data/words_to_learn.csv`
  * ユーザーが習得（✔）した単語を除外した最新リストを自動永続化。

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 非同期タイマーの競合・残存防御 (Timer Interlock)
* カード表示から自動で裏返るまでの遅延時間を **3000ミリ秒（3秒）** とする。
* **残存タイマーの破棄制約**:
  * 3秒経過前にユーザーが「✔」または「✖」ボタンを押下した場合、スケジュール済みの `flip_timer` を `window.after_cancel(flip_timer)` で確実に破棄する。
  * 破棄を怠った場合、新しいカードが表示された直後に古いタイマーが暴発して即座に裏返る同期ズレ（競合状態）が発生するため、これを厳格に防止する。

### 2.2 ファイル読み込みの境界例外 (Fallback Flow)
* 起動時、`words_to_learn.csv` の存在を優先的に確認。
* **例外捕捉**:
  * `FileNotFoundError` または空ファイルによる `pd.errors.EmptyDataError` 発生時:
    * 例外を捕捉し、初期マスター `french_words.csv` から全単語をロードして学習リストを初期化する。

### 2.3 全単語習得（リスト枯渇）の境界値
* 単語リストの残数が 0（`len(to_learn) == 0`）に達した場合:
  * `random.choice()` の実行による `IndexError` を防止する境界ガード。
  * Canvas上に完了メッセージ（例: タイトル `"Congratulations!"`, 単語 `"You learned all words!"`）を描画し、操作ボタンを無効化（または非活性）にする。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 状態遷移 (State Machine)
システムは以下のカードサイクルを遷移する。

```
[INIT: データ読込 (words_to_learn or french_words)]
   |
   v
[FRONT: 表面表示] <---------------------------------------------+
   ・カード背景: card_front.png                                 |
   ・言語: "French" (black)                                      |
   ・単語: ランダム抽出したフランス語 (black)                   |
   ・3秒タイマーセット (flip_timer = window.after(3000, flip))   |
   |                                                            |
   +---> (3秒経過: flip_timer 発火)                             |
   |           |                                                |
   |           v                                                |
   |     [BACK: 裏面表示]                                       |
   |     ・カード背景: card_back.png                            |
   |     ・言語: "English" (white)                              |
   |     ・単語: 英語対訳 (white)                               |
   |                                                            |
   +---> (ユーザー操作: ✖押下)                                  |
   |     ・after_cancel(flip_timer) ----------------------------+
   |     ・単語は保持したまま次のカードへ
   |
   +---> (ユーザー操作: ✔押下)
         ・after_cancel(flip_timer)
         ・to_learn.remove(current_card)
         ・words_to_learn.csv へ保存
         ・(残数 > 0) ------------------------------------------+
         ・(残数 == 0) ---> [ALL_LEARNED: 完了表示]
```

### 3.2 データ構造と更新アルゴリズム
1. **辞書リスト形式への変換**:
   ```python
   to_learn: list[dict[str, str]] = df.to_dict(orient="records")
   ```
2. **習得時の差分更新 (`is_known`)**:
   ```python
   to_learn.remove(current_card)
   pd.DataFrame(to_learn).to_csv("data/words_to_learn.csv", index=False)
   next_card()
   ```

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 アセット整合性
* `card_front.png`, `card_back.png`, `right.png`, `wrong.png` が存在しない場合、クラッシュを防止し、コンソールに分かりやすいエラーを出力して終了する。

### 4.2 文字エンコーディングの担保
* フランス語の特殊文字（`é`, `è`, `ç` 等）を正確に保持するため、入出力時のエンコーディングを明示的に `utf-8` に統一する。

---

## 5. モジュール構成 (Architecture)

```
flash-card-project/
├── data/
│   ├── french_words.csv     # 初期フランス語-英語マスターデータ
│   └── words_to_learn.csv   # (自動生成) 復習用未習得単語リスト
├── images/
│   ├── card_back.png        # カード裏面画像 (800x526)
│   ├── card_front.png       # カード表面画像 (800x526)
│   ├── right.png            # 正解ボタン (✔)
│   └── wrong.png            # 不正解ボタン (✖)
├── main.py                  # Tkinter UI、タイマー制御、データ更新統括
└── requirements.txt         # 依存ライブラリ (pandas)
```
