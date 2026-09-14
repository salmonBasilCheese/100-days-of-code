# 100 Days of Code: Python Learning Projects

Udemy講座「100 Days of Code: The Complete Python Pro Bootcamp」の実践リポジトリです。
基礎構文からOOP、GUI、Web API連携、Webスクレイピング、ブラウザ自動化（Selenium）までを網羅的に実装しています。

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

### 4. Webスクレイピング & ブラウザ自動化 (BeautifulSoup / Selenium)
| プロジェクト名 | 概要 | 主な技術・ライブラリ |
| :--- | :--- | :--- |
| **`cookie_clicker_bot`** | クッキークリッカーの自動プレイおよび最適アップグレード購入Bot | `selenium`, DOM走査, タイマー制御 |
| **`tinder_swiping_bot`** | 認証ログインおよびマッチングアプリの自動スワイプ・例外ハンドリングBot | `selenium`, モーダル破棄, 例外処理 |
| **`speed_bot`** | Speedtestで回線速度を自動計測し、閾値に応じて投稿サービスへ自動報告 | `selenium`, `WebDriverWait`, 非同期測定検知 |
| **`insta_clone_follower`** | ターゲットユーザーのフォロワーモーダルをスクロールし、順次フォロー | `selenium`, 局所スクロール, 状態フィルタリング |
| **`data_entry_bot`** | Zillowクローンから物件情報をスクレイピングし、Googleフォームへ自動転記 | `beautifulsoup4`, `requests`, `selenium`, 正規表現 |

---

## 🛠 開発環境・セットアップ

### 必要要件
* Python 3.10 以上
* Google Chrome および対応バージョンの ChromeDriver (Selenium Managerにより自動解決)
* 各プロジェクトフォルダごとの `requirements.txt` / `.env`

### 基本セットアップ
```bash
# 仮想環境の作成と有効化
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1

# プロジェクトごとの依存パッケージインストール (例: selenium_automation)
pip install -r selenium_automation/requirements.txt