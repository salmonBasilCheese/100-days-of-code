# 目的
Open Trivia DBのデータを用いて、CLIで動作するTrue/False形式のクイズゲームを実装してください。
設計品質と保守性を担保するため、以下のアーキテクチャおよび要件を厳格に遵守してください。

# ファイル構成と責務の分離
1. `question_model.py`
   - `Question` クラスを定義。
   - 責務: 1問分の問題文（text）と正解（answer）のデータを保持するモデル。
2. `quiz_brain.py`
   - `QuizBrain` クラスを定義。
   - 責務: クイズの進行管理（現在の問題番号、スコア管理、次問の出題、回答の判定）。外部からリストで `Question` オブジェクト群を受け取る設計にすること。
3. `data.py`
   - Open Trivia DB から取得した問題リスト（各要素は `"question"` と `"correct_answer"` を含む辞書）を `question_data` 変数として保持。
4. `main.py`
   - エントリーポイント。`data.py` のデータを `Question` オブジェクトのリストへ変換し、`QuizBrain` に渡して実行ループを制御する。

# 必須要件と例外・境界値処理
1. **テキストのデコード処理**:
   - Open Trivia DB 特有のHTMLエンティティ（例: `&quot;`, `&#039;` など）が含まれるため、`html.unescape()` を使用して可読な文字列にデコードして表示すること。
2. **入力バリデーション（異常系）**:
   - ユーザー入力が 'True' / 'False'（大文字小文字不問、't'/'f'の省略形も許容）以外の場合はエラーメッセージを表示し、有効な値が入力されるまで再入力を要求すること。
3. **終了条件（境界値・IndexError対策）**:
   - リストの末尾に達した際、`IndexError` を発生させず `has_more_questions()` メソッド等で安全にループを終了させること。
   - 終了時は「クイズ完了」の旨と「最終スコア（例: You completed the quiz! Your final score was: 10/12）」を表示すること。