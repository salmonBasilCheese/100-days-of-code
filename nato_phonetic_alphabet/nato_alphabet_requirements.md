# システム要件定義書: NATO Phonetic Alphabet Converter (Day 26 / Day 30)

## 1. 主語・インターフェース (Actors, Dimensions & Interfaces)

### 1.1 実行環境およびインターフェース形式
* **インターフェース**: コマンドラインインターフェース (CLI)
* **GUI**: なし（標準入出力 `input()` / `print()` で完結）
* **依存ライブラリ**: `pandas`

### 1.2 データソース (Data Source)
* **入力ファイル**: `nato_phonetic_alphabet.csv`
* **スキーマ構成**: 全26行、ヘッダー `letter,code`
  * `letter` (str): 英大文字 1文字 (`A` 〜 `Z`)
  * `code` (str): NATOフォネティックコード単語 (`Alfa`, `Bravo`, etc.)

### 1.3 操作および入出力インターフェース
* **プロンプト入力**:
  * `input("Enter a word (or 'exit' to quit): ")`
* **入力文字列の正規化**:
  * 入力文字列 $S$ に対し、大文字変換を適用:
    $$S_{\text{upper}} = S.\text{upper}()$$
* **終了コマンド**:
  * ユーザー入力が `"EXIT"` または `"QUIT"`（前後の空白を除去して大文字化したもの）の場合、変換処理を行わず正常終了する。
* **出力形式**:
  * 変換結果の NATO コード単語のリスト `list[str]` をコンソールに表示。
  * 例: 入力 `"Cat"` $\implies$ 出力 `['Charlie', 'Alfa', 'Tango']`

---

## 2. 境界制約 (Boundary Conditions & Invariants)

### 2.1 空白文字（スペース）の扱い
* 単語間や前後のスペース（`" "`）はアルファベット以外の異常値とはみなさず、スキップ（除外）する。
* 例: `"HE LO"` $\implies$ スペースを読み飛ばし、`['Hotel', 'Echo', 'Lima', 'Oscar']` を生成。

### 2.2 アルファベット以外の文字（異常値防御）
* 数字（`0-9`）、特殊記号（`!`, `@`, `-` 等）、全角文字、日本語などが含まれている場合:
  * 辞書参照時に `KeyError` が発生する。
  * `try-except KeyError` ブロックにより捕捉し、プログラムをクラッシュさせずに警告メッセージを出力して再入力を促す。
  * エラーメッセージ: `"Sorry, only letters in the alphabet please."`

### 2.3 空入力（Empty String）の制約
* 文字列が空（スペースのみ、または即座にEnter）の場合:
  * 無効入力として扱い、再度プロンプトを表示する。

---

## 3. 操作・ロジック仕様 (State Machine & Logic)

### 3.1 状態遷移 (State Machine)
システムは以下のループ制御ステートマシンとして動作する。
1. `INIT`: CSV読み込み、Pandasからネイティブ辞書 `{letter: code}` の生成。
2. `INPUT`: ユーザーからのテキスト入力待機。
3. `CHECK_COMMAND`: 終了コマンド（`EXIT`/`QUIT`）の判定 $\implies$ 合致時は `TERMINATE` へ。
4. `CONVERT`: 空白を除外した文字の NATO コード変換（内包表記と `try-except`）。
5. `SUCCESS`: 変換リストの表示 $\implies$ 再び `INPUT` へ。
6. `ERROR`: `KeyError` 捕捉、エラー告知 $\implies$ 再び `INPUT` へ。
7. `TERMINATE`: 終了メッセージ出力、正常離脱。

```
[INIT: 辞書生成]
   |
   v
[INPUT] <------------------------------------+
   |                                         |
   +---> (終了コマンド: "EXIT" / "QUIT") ---> [TERMINATE]
   |
   +---> [CONVERT: リスト内包表記]
           |
           +---> (成功: 全文字が辞書に存在) ----> [SUCCESS: 出力] ---+
           |                                                      |
           +---> (失敗: KeyError 捕捉) ------> [ERROR: 警告] ------+
```

### 3.2 データ構造と探索アルゴリズム
1. **辞書構築 (初期化時に1度のみ実行)**:
   * 計算量: $O(1)$ 参照を実現するため、Pandas の DataFrame から辞書内包表記でネイティブ `dict[str, str]` を生成する。
   ```python
   nato_dict: dict[str, str] = {row.letter: row.code for (_, row) in df.iterrows()}
   ```
2. **変換アルゴリズム (リスト内包表記)**:
   * 空白文字をスキップしつつ、各文字を辞書から参照する。
   ```python
   output_list: list[str] = [nato_dict[letter] for letter in word if letter != " "]
   ```
   * 1文字でも辞書にない文字が含まれていれば `KeyError` が送出され、アトミックに `except` 節へ制御が移行する。

---

## 4. 例外・非機能要件 (Robustness & Non-Functional Requirements)

### 4.1 ファイルI/Oの堅牢性
* `nato_phonetic_alphabet.csv` が存在しない場合、`FileNotFoundError` をキャッチして明確なエラーメッセージを出力し、異常終了を防ぐ。

### 4.2 再試行ループ制御
* 変換失敗時および成功時にプロセスを終了させず、終了コマンドが明示的に渡されるまで安全に対話を継続する `while True` ループ構造。
* ユーザーによる強制割り込み（`KeyboardInterrupt` / `Ctrl+C`）発生時もトレースバックを出力せず、安全にメッセージを表示して終了する。

---

## 5. モジュール構成 (Architecture)

```
nato_alphabet/
├── nato_phonetic_alphabet.csv   # アルファベットとコードのマスターデータ
├── main.py                     # 辞書構築、変換ロジック、CLIループ制御
└── requirements.txt            # 依存パッケージ (pandas)
```
