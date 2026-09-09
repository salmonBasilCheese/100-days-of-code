from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import requests

# main.py と同階層にある .env を明示的に読み込む
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

STOCK = "NVDA"
COMPANY_NAME = "NVIDIA Corporation"

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
THRESHOLD_PERCENT = float(os.environ.get("VOLATILITY_THRESHOLD", "5.0"))

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"


def check_environment() -> None:
    """必須環境変数の存在を検証する。"""
    missing_vars = []
    if not ALPHA_VANTAGE_API_KEY:
        missing_vars.append("ALPHA_VANTAGE_API_KEY")
    if not NEWS_API_KEY:
        missing_vars.append("NEWS_API_KEY")
    if not DISCORD_WEBHOOK_URL:
        missing_vars.append("DISCORD_WEBHOOK_URL")

    if missing_vars:
        print(
            f"[Fatal Error] Missing required environment variables: {', '.join(missing_vars)}",
            file=sys.stderr,
        )
        sys.exit(1)


def get_stock_volatility() -> tuple[bool, float, str]:
    """
    Alpha Vantage から直近2営業日の終値を取得し、変動率を計算する。
    戻り値: (閾値超過フラグ, 変動率%, 方向シンボル '🔺' または '🔻')
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "compact",
    }

    response = requests.get(STOCK_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # レート制限・API例外の検知
    if "Note" in data:
        print(f"[Rate Limit Exceeded] Alpha Vantage: {data['Note']}", file=sys.stderr)
        sys.exit(1)
    if "Information" in data:
        print(f"[API Notice] Alpha Vantage: {data['Information']}", file=sys.stderr)
        sys.exit(1)

    time_series = data.get("Time Series (Daily)")
    if not time_series:
        print(f"[Error] Unexpected API response: {data}", file=sys.stderr)
        sys.exit(1)

    # 日付キーを降順ソートして最新2営業日を取得（祝日・週末の欠落を吸収）
    sorted_dates = sorted(time_series.keys(), reverse=True)
    if len(sorted_dates) < 2:
        print("[Error] Not enough trading data available.", file=sys.stderr)
        sys.exit(1)

    latest_date = sorted_dates[0]
    previous_date = sorted_dates[1]

    latest_close = float(time_series[latest_date]["4. close"])
    previous_close = float(time_series[previous_date]["4. close"])

    delta = latest_close - previous_close
    diff_percent = (abs(delta) / previous_close) * 100
    direction_symbol = "🔺" if delta >= 0 else "🔻"

    print(
        f"[Market Data] {STOCK} | {previous_date}: ${previous_close:.2f} -> "
        f"{latest_date}: ${latest_close:.2f} ({direction_symbol}{diff_percent:.2f}%)"
    )

    is_triggered = diff_percent >= THRESHOLD_PERCENT
    return is_triggered, diff_percent, direction_symbol


def get_company_news() -> list[dict]:
    """NewsAPI から会社名に関する直近上位 3 件のニュースを取得する。"""
    params = {
        "q": "NVIDIA",
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 3,
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(NEWS_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()
    news_data = response.json()

    return news_data.get("articles", [])[:3]


def send_discord_notification(message: str) -> None:
    """Discord Webhook へメッセージを送信する。"""
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()


def main() -> None:
    check_environment()

    try:
        is_triggered, diff_percent, symbol = get_stock_volatility()

        if not is_triggered:
            print(
                f"[Skip] {STOCK} change ({diff_percent:.2f}%) is below the {THRESHOLD_PERCENT}% threshold. "
                "Notification skipped."
            )
            return

        print(
            f"[Trigger] Volatility threshold reached: {symbol}{diff_percent:.2f}%. "
            "Fetching news..."
        )
        articles = get_company_news()

        if not articles:
            print("[Warning] No news articles found.")
            return

        for article in articles:
            title = article.get("title", "No Title")
            description = article.get("description", "No Description")
            url = article.get("url", "")

            # コース指定のメッセージレイアウト
            message = (
                f"**{STOCK}: {symbol}{diff_percent:.2f}%**\n"
                f"**Headline**: {title}\n"
                f"**Brief**: {description}\n"
                f"**URL**: {url}"
            )
            send_discord_notification(message)
            print(f"[Success] Dispatched news alert: {title}")

    except requests.exceptions.RequestException as e:
        print(f"[Network Error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
