# システム要件定義書: Pomodoro Timer (Day 28)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 画面およびウィンドウ仕様 (Window & Layout)
* **GUIフレームワーク**: Python標準 `tkinter`
* **ウィンドウ背景色**: `YELLOW = "#f7f5dd"`
* **ウィンドウパディング**: `padx=100, pady=50`
* **ウィンドウタイトル**: `"Pomodoro"`
* **レイアウト方式**: `grid()`（列: 0〜2、行: 0〜3）

### 1.2 カラーパレット (Theme Colors)
* `YELLOW = "#f7f5dd"` (背景色)
* `GREEN = "#9bdeac"` (Work時タイトル、Startボタン/チェックマーク)
* `PINK = "#e2979c"` (Short Break時タイトル)
* `RED = "#e7305b"` (Long Break時タイトル)

### 1.3 タイマー設定値 (Session Durations)
* **Work (作業)**: 25分 ($25 \times 60 = 1500$ 秒)
* **Short Break (短休憩)**: 5分 ($5 \times 60 = 300$ 秒)
* **Long Break (長休憩)**: 20分 ($20 \times 60 = 1200$ 秒)
* ※ テスト用ファストモード（例: 10秒 / 2秒 / 5秒）への切り替えが容易な定数構造とする。

### 1.4 ウィジェット仕様 (Widgets & Grid Matrix)
1. **Title Label (行0, 列1)**:
   * テキスト: 初期 `"Timer"` (状態に応じて `"Work"`, `"Break"` に変化)
   * フォント: `("Courier", 50, "bold")`
   * 背景色: `YELLOW`, 文字色: `GREEN` (Work時), `PINK` (Short Break時), `RED` (Long Break時)
2. **Canvas (行1, 列1)**:
   * サイズ: 幅 200px × 高さ 224px
   * 背景色: `YELLOW`, `highlightthickness=0` (枠線除去)
   * 画像要素: `tomato.png` (中心 `(100, 112)`)
   * テキスト要素: 初期 `"00:00"`, 座標 `(100, 130)`, 文字色 `"white"`, フォント `("Courier", 35, "bold")`
3. **Start Button (行2, 列0)**:
   * テキスト: `"Start"`, フォント `("Courier", 10, "bold")`, `highlightthickness=0`
   * アクション: `start_timer()`
4. **Reset Button (行2, 列2)**:
   * テキスト: `"Reset"`, フォント `("Courier", 10, "bold")`, `highlightthickness=0`
   * アクション: `reset_timer()`
5. **Checkmark Label (行3, 列1)**:
   * テキスト: 初期 `""` (完了したWorkセッション数に応じ `"✔"` を蓄積)
   * 文字色: `GREEN`, 背景色: `YELLOW`, フォント `("Arial", 16, "bold")`

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 多重タイマー起動のインターロック制御
* Startボタンが連打された場合、複数の `window.after()` スレッドが多重起動し、カウントダウンが2倍・3倍速になる物理破綻が発生する。
* **排他制御制約**:
  * タイマー稼働中（`is_running == True` または `timer is not None`）は、Startボタンの追加入力を完全に無視（無効化）する。

### 2.2 リセット時の完全破棄 (Cancellation Invariant)
* Resetボタン押下時、登録されている非同期コールバックを `window.after_cancel(timer)` で確実に破棄する。
* 破棄後、以下の状態を確定初期化（アトミック初期化）する:
  * タイマーID: `timer = None`
  * レップ数: `reps = 0`
  * 稼働フラグ: `is_running = False`
  * 画面表示: タイトル `"Timer"`, カウント `"00:00"`, チェックマーク `""`

### 2.3 カウントゼロ到達時の境界値
* 残り秒数が $0$ に到達した瞬間 (`count == 0`):
  * カウントダウンを停止し、即座に次のセッションへの状態遷移を実行する。
  * 負の数値 (`count < 0`) への突入を厳格に禁止する。

### 2.4 ゼロ埋めフォーマット境界 (Zero-padding)
* 表示文字列生成時、秒数が $10$ 未満（$0 \le 	ext{sec} \le 9$）の場合は、必ず `f"{sec:02d}"` 形式で2桁ゼロ埋めを行う。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 状態遷移 (State Machine)
システムは以下の8ステップ（1サイクル）を周期的に遷移する。
* `reps`: 実行中セッションのインデックス（$1 \le 	ext{reps} \le 8$）

| reps | セッション種別 | 時間設定 | タイトル表示 | タイトル色 | チェックマーク更新 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Work 1 | 25分 (1500s) | `"Work"` | GREEN | なし |
| 2 | Short Break 1 | 5分 (300s) | `"Break"` | PINK | ✔ (1個) |
| 3 | Work 2 | 25分 (1500s) | `"Work"` | GREEN | - |
| 4 | Short Break 2 | 5分 (300s) | `"Break"` | PINK | ✔✔ (2個) |
| 5 | Work 3 | 25分 (1500s) | `"Work"` | GREEN | - |
| 6 | Short Break 3 | 5分 (300s) | `"Break"` | PINK | ✔✔✔ (3個) |
| 7 | Work 4 | 25分 (1500s) | `"Work"` | GREEN | - |
| 8 | Long Break | 20分 (1200s) | `"Break"` | RED | ✔✔✔✔ (4個) |

```
[IDLE: Timer / 00:00]
   | (Startボタン押下: is_running=False のみ受付)
   v
[WORK: reps=1, 3, 5, 7] <-----------------------+
   |                                            |
   +---> (count == 0: 完了)                     |
           |                                    |
           v                                    |
     [SHORT BREAK: reps=2, 4, 6] ---------------+
     ・チェックマーク追加 (floor(reps/2))
     ・ウィンドウ最前面通知
           |
           +---> (reps == 8 の場合)
                   |
                   v
             [LONG BREAK: reps=8]
             ・チェックマーク追加 (4個)
             ・ウィンドウ最前面通知
                   |
                   +---> (完了後 reps=0 へループ)
```

### 3.2 チェックマーク算出ロジック
* チェックマークの個数は、完了した作業セッション数に厳密に一致する:
  $$\text{num\_checks} = \lfloor \frac{\text{reps}}{2} \rfloor$$
* Break開始時にチェックマーク文字列 `"✔" * num_checks` を再描画。

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 アセット依存性
* `tomato.png` がカレントディレクトリに存在しない場合、プログラムがクラッシュしないようファイル存在確認を行い、欠損時はプレースホルダーの円形描画または明示的な例外メッセージを出力する。

### 4.2 非同期更新精度 (`after()` 制御)
* `time.sleep()` の使用はGUIメインスレッドをフリーズ（応答なし）させるため完全禁止。
* `window.after(1000, count_down, count - 1)` を用いて1秒ごとに非同期コールバックを実行する。

### 4.3 ウィンドウフォーカス復帰（デスクトップ通知代用）
* 作業から休憩、あるいは休憩から作業への切り替え時（`count == 0`）、ユーザーが他アプリを操作している場合を考慮し、ウィンドウを一時的に最前面へポップアップ表示する:
  ```python
  window.attributes('-topmost', 1)
  window.attributes('-topmost', 0)
  ```

---

## 5. モジュール構成 (Architecture)

```
pomodoro_timer/
├── tomato.png      # トマトイラスト画像 (200x224)
├── main.py         # Tkinter UI構築、タイマー状態遷移統括
└── requirements.txt# 依存ライブラリなし (Python標準ライブラリのみ)
```
