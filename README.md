# 100 Days of Code: Python Portfolio

Pythonによる基礎プログラミング、OOP、GUIアプリケーション、データ処理、およびCI/CDタスク自動化の実践ポートフォリオです。

## プロジェクト一覧

### Phase 1: 基礎・OOP・コンソール
* **coffee_machine**: オブジェクト指向設計によるコーヒーマシンシミュレータ
* **quiz_brain**: クラス設計とオープンAPIを利用したクイズシステム

### Phase 2: Turtle グラフィックス & アーケードゲーム
* **etch_a_sketch**: イベントリスナーを用いたスケッチアプリ
* **hirst_painting**: RGBタプル抽出とグリッド描画によるスポットペインティング
* **turtle_race**: 乱数と座標制御によるタートルレースゲーム
* **snake_game**: セグメント制御、衝突判定、および排他制御を組み込んだスネークゲーム
* **pong_game**: パドル反射とスコアボード管理を実装したクラシックPong
* **turtle_crossing**: 車両生成と速度スケーリングによるカエルの道路横断ゲーム

### Phase 3: データ処理 & GUI アプリケーション (Tkinter / Pandas)
* **us_states_quiz**: PandasデータフレームとTurtle座標を連携した地図クイズ
* **nato_phonetic_alphabet**: 辞書内包表記とKeyError例外ハンドリングによるフォネティック変換
* **pomodoro_timer**: `after()` による非同期カウントダウンと排他制御を備えたポモドーロタイマー
* **password_manager**: JSONデータ永続化、暗号化パスワード生成、クリップボード連携
* **flash_card_project**: 非同期フリップタイマーとPandasによる進捗永続化フラッシュカード

### Phase 4: 自動化 & CI/CD
* **birthday_wisher**: 
  * `smtplib` + Gmail STARTTLS によるメール配信
  * ゼロ件境界防御、手動日付テストモード（`--date`）
  * GitHub Actions による JST 07:00 定期実行（Cron）および手動トリガー（`workflow_dispatch`）