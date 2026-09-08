# システム要件定義書: U.S. States Quiz (Day 25)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 画面およびマップ構成 (Screen & Map)
* **解像度**: 幅 725px × 高さ 491px（アメリカ合衆国白地図画像 `blank_states_img.gif` のアスペクト比・解像度に完全一致）
* **背景画像**: `blank_states_img.gif`
  * Turtleの `screen.addshape("blank_states_img.gif")` を登録し、背景として描画。
* **座標系**: 原点 `(0, 0)` を画面中央とするデカルト座標系
  * X軸: `[-362, 362]`
  * Y軸: `[-245, 245]`
* **タイトル**: `"U.S. States Quiz"`

### 1.2 データソース (Data Source)
* **入力データファイル**: `50_states.csv`
  * レコード構成: 全50州（ヘッダー: `state,x,y`）
  * 列定義:
    * `state` (string): 州名（例: `"Alabama"`, `"New York"`）
    * `x` (int): 州の中心X座標
    * `y` (int): 州の中心Y座標
  * データ処理ライブラリ: **Pandas** を使用して読み込みおよび差分抽出を行う。

### 1.3 操作および入力インターフェース (Input Interface)
* **回答入力**:
  * `screen.textinput(title=..., prompt=...)` を利用したモーダルダイアログ。
  * **ダイアログタイトル**: 進捗状況を表示（例: `"{score}/50 States Correct | Time Left: {mm}:{ss}"`）。
  * **プロンプト文**: `"What's another state's name?"`
* **表記揺れの吸収（正規化）**:
  * ユーザー入力文字列 $S$ に対し、前後空白除去とタイトルケース変換を施す:
    $$S_{\text{normalized}} = S.\text{strip}().\text{title}()$$
  * 例: `"new york"`, `"NEW YORK"`, `"  New York  "` はすべて `"New York"` として判定。
* **特殊コマンド**:
  * `"Exit"` または `"Quit"`: クイズを途中でギブアップ・終了し、未正解リストを出力して終了シーケンスへ遷移。

### 1.4 タイマーおよびスコアボードインターフェース (Timer & Scoreboard)
* **制限時間**: **10分間（600秒）**（Sporcle準拠の標準設定）。
* **タイマー表示**:
  * 画面右上隅（例: `(230, 210)`）に書き込み用Turtleを配置し、`mm:ss` 形式で残り時間をリアルタイム更新。
* **地図上への州名描画 (State Pen)**:
  * 正解判定時、該当州の `(x, y)` 座標へTurtleを移動させ、州名をテキスト描画。
  * フォント仕様: Arial, 8pt, normal

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 スコアおよび状態の不変条件
* **正解数制約**:
  $$0 \le \text{score} \le 50$$
* **重複回答の禁止**:
  * 正解済みの州は `guessed_states: list[str]`（または `set[str]`）に記録。
  * 既に `guessed_states` に含まれる州名が入力された場合、スコア加算・再描画は行わず、無効入力として処理（多重カウント禁止）。

### 2.2 時間境界と終了条件
* **制限時間切れ**:
  $$\text{elapsed\_time} \ge 600.0\text{秒}$$
  * 時間切れとなった瞬間にクイズを強制終了し、未回答データの自動出力へ移行する。
* **全問正解**:
  $$\text{score} == 50$$
  * 50州すべてを回答した瞬間にクイズクリアとし、勝利告知を描画して正常終了。

### 2.3 入力キャンセル・中断の境界処理
* `screen.textinput()` でユーザーが「Cancel」ボタンを押下した場合（戻り値が `None`）、例外 `AttributeError` を投げずに安全に途中離脱シーケンス（ギブアップ）を通す。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 状態遷移 (State Machine)
システムは以下の状態を持つステートマシンとして動作する。
1. `READY`: CSVデータ読み込み、画面・背景セットアップ、タイマー初期化。
2. `PLAYING`: 入力受付、正解判定、地図描画、タイマー減算ループ。
3. `FINISHED`: 全問正解、クリア告知表示。
4. `TIME_UP`: 制限時間切れ、タイムアップ告知表示。
5. `EXIT_EARLY`: ユーザーによる `"Exit"` 入力またはキャンセル。
6. `EXPORT`: `FINISHED` 以外の終了時、未回答州を抽出しCSVへ自動出力。

```
[READY]
   |
   v
[PLAYING] <---------------------------------------------+
   |                                                    |
   +---> (入力判定: 正解 かつ 未回答)                     |
   |           |                                        |
   |           v                                        |
   |     ・地図上に州名描画                             |
   |     ・guessed_states に追加                        |
   |     ・score += 1                                   |
   |     ・(score < 50) --------------------------------+
   |     ・(score == 50) ---> [FINISHED]
   |
   +---> (時間切れ: elapsed >= 600s) -------> [TIME_UP] ---> [EXPORT]
   |
   +---> (コマンド: "Exit" or Cancel) ------> [EXIT_EARLY] -> [EXPORT]
```

### 3.2 Pandasによる探索・データ抽出ロジック
* 正解判定時:
  ```python
  state_data = df[df["state"] == answer_state]
  if not state_data.empty:
      x = int(state_data["x"].iloc[0])
      y = int(state_data["y"].iloc[0])
  ```
* 未正解データの抽出とCSV出力ロジック:
  ```python
  # 集合の差分演算による抽出
  all_states = df["state"].to_list()
  missing_states = [state for state in all_states if state not in guessed_states]
  df_missing = pd.DataFrame(missing_states, columns=["state"])
  df_missing.to_csv("states_to_learn.csv", index=False)
  ```

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 ファイルI/Oの堅牢性
* `50_states.csv` および `blank_states_img.gif` が存在しない場合、システムがクラッシュせず `"Data file not found"` 等の明確なエラーメッセージをコンソールに出力して安全終了する。
* 学習用CSV `states_to_learn.csv` の書き込み時にエンコーディングは `utf-8` を明示指定。

### 4.2 UI描画と非同期タイマー制御
* `textinput()` はブロッキング関数（ユーザーの入力完了まで処理が停止する）であるため、Turtle標準の単一スレッドループではタイマーが入力中に停止する。
* **タイマー精度の保証アプローチ**:
  * 各入力ステップの前後に `time.time()` を取得し、総経過時間を厳密に計算（タイムスタンプ差分方式）。
  * 入力ダイアログを開く直前に残り時間を逆算してダイアログタイトル（例: `Time Left: 08:42`）に反映。
  * 入力完了時に制限時間を超過していた場合、直ちに `TIME_UP` ステートへ遷移する。

### 4.3 異常終了のハンドリング
* ウィンドウの「×」閉じに伴う `turtle.Terminator` / `tk.TclError` をキャッチし、トレースバックをコンソールに吐き出さずにプロセスを終了する。

---

## 5. モジュール構成 (Architecture)

```
us_states_quiz/
├── 50_states.csv            # 州名と座標マスターデータ
├── blank_states_img.gif     # アメリカ白地図画像
├── main.py                  # メインロジック、Pandas連携、Turtle制御統括
├── states_to_learn.csv      # (自動生成) 復習・学習用未回答州リスト
└── requirements.txt         # 依存ライブラリ (pandas)
```
