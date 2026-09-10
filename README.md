# 100 Days of Code: Python Learning Projects

Udemy講座「100 Days of Code: The Complete Python Pro Bootcamp」の実践リポジトリです。
基礎構文からOOP、GUI、Web API連携、Webスクレイピング、自動化スクリプトまでを網羅的に実装しています。

---

## 📂 プロジェクト一覧

### 1. Game & GUI アプリケーション (Tkinter / Turtle)
| プロジェクト名 | 概要 | 主な技術・ライブラリ |
| :--- | :--- | :--- |
| **`coffee_machine`** | オブジェクト指向 (OOP) で設計したコーヒー自動販売機シミュレータ | Python OOP |
| **`hirst_painting`** | ダミアン・ハーストのドット絵を再現するジェネレーティブアート | `turtle`, `colorgram.py` |
| **`etch_a_sketch`** | キーボード入力イベントで描画するエッチ・ア・スケッチ | `turtle` イベントリスナー |
| **`turtle_race`** | タートルを用いたランダム着順レースゲーム | `turtle`, `random` |
| **`snake_game`** | クラシックなヘビゲーム（スコア永続化・ハイスコア保存機能付き） | `turtle`, OOP, File I/O |
| **`pong_game`** | 2プレイヤー対応のアーケードPongゲーム | `turtle`, OOP |
| **`turtle_crossing`** | 車を避けて道路を横断するフロッガー風ゲーム | `turtle`, OOP |
| **`us_states_quiz`** | アメリカ50州の名称・位置を当てるマップクイズ | `turtle`, `pandas`, CSV |
| **`pomodoro_timer`** | 集中と休憩のサイクルを管理するポモドーロタイマーGUI | `tkinter` |
| **`password_manager`** | パスワード自動生成・クリップボードコピー・JSON保存ツール | `tkinter`, `json`, 例外処理 |
| **`flash_card_project`** | 未暗記単語をトラッキングする単語フラッシュカードアプリ | `tkinter`, `pandas` |

---

### 2. データ処理 & CLI ツール
| プロジェクト名 | 概要 | 主な技術・ライブラリ |
| :--- | :--- | :--- |
| **`nato_phonetic_alphabet`** | 単語をNATOフォネティックコードへ変換するCLIツール | `pandas`, 辞書内包表記, 例外処理 |
| **`quiz_brain`** | Open Trivia DB API を活用したCLIクイズアプリ | API, クラス設計 |
| **`quiz_brain_gui`** | `quiz_brain` にTkinter製GUIを統合したクイズアプリ | `tkinter`, `requests`, HTMLエンティティデコード |

---

### 3. Web API 連携 & 自動化通知システム
| プロジェクト名 | 概要 | 主な技術・ライブラリ |
| :--- | :--- | :--- |
| **`kanye_quotes`** | Kanye Rest API からランダムな名言を取得・描画するGUI | `tkinter`, `requests` |
| **`birthday_wisher`** | 当日の誕生日に応じて自動で祝辞メールを送信するバッチスクリプト | `smtplib`, `datetime`, `pandas` |
| **`iss_overhead_notifier`** | 国際宇宙ステーション (ISS) が上空を通過した際にメール通知 | `requests`, `smtplib`, 緯度経度計算 |
| **`rain_alert`** | OpenWeatherMap API を用いて当日降水予報時にSMS通知 | `requests`, Twilio SMS API |
| **`stock_news_alert`** | 株価の急変動（±5%以上）検知時に最新ニュースをSMS配信 | Alpha Vantage, NewsAPI, Twilio |
| **`habit_tracker`** | Pixela API を使用した習慣（学習・作業量）の草生やしトラッカー | Pixela API, HTTP headers/auth |
| **`flight_deal_finder`** | Google Flights (SerpAPI) の最安値を監視し、Discord / メールへ一斉通知 | SerpAPI, Sheety API, `smtplib`, `requests-cache` |

---

## 🛠 開発環境・セットアップ

### 必要要件
* Python 3.10 以上
* 各プロジェクトフォルダごとの `requirements.txt` / `.env`

### 基本セットアップ
```bash
# 仮想環境の作成と有効化
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1

# プロジェクトごとの依存パッケージインストール (例: flight_deal_finder)
pip install -r flight_deal_finder/requirements.txt

### 環境変数管理
APIキーや認証情報を含む各プロジェクト（`flight_deal_finder`, `stock_news_alert` 等）には `.env.example` が配置されています。
各ディレクトリに `.env` を作成し、必要なキーを設定してください。

---

## 🔒 セキュリティとGit管理
* 秘密情報（`.env`）およびローカルキャッシュ（`*.sqlite`, `*.pyc` 等）は `.gitignore` にて追跡から除外されています。