from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import requests

# main.py と同じフォルダにある .env を明示的に指定して読み込む
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# 設定値・機密情報の取得
OWM_API_KEY = os.environ.get("OWM_API_KEY")
LAT = os.environ.get("LAT", "35.6895")
LON = os.environ.get("LON", "139.6917")

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"


def check_environment() -> None:
    """必須環境変数の存在を検証する。"""
    if not OWM_API_KEY:
        print(
            "[Fatal Error] Environment variable 'OWM_API_KEY' is missing.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not DISCORD_WEBHOOK_URL and not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        print(
            "[Warning] Neither Discord Webhook nor Telegram Bot credentials are configured. "
            "Alerts cannot be dispatched.",
            file=sys.stderr,
        )


def will_it_rain() -> tuple[bool, list[str]]:
    """
    OpenWeatherMap から直近12時間（4スライス）の天気を取得し、降水の有無を判定する。
    戻り値: (降水有無フラグ, 検知された気象説明リスト)
    """
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": OWM_API_KEY,
        "cnt": 4,  # 3時間 × 4 = 12時間
    }

    response = requests.get(OWM_ENDPOINT, params=params, timeout=10)
    response.raise_for_status()
    weather_data = response.json()

    forecast_slice = weather_data.get("list", [])
    rain_descriptions = []

    for item in forecast_slice:
        condition_code = item["weather"][0]["id"]
        # 気象コード 700 未満は降水系イベント（雷雨、霧雨、雨、雪）
        if condition_code < 700:
            desc = item["weather"][0]["description"]
            rain_descriptions.append(f"{desc} (code: {condition_code})")

    return (len(rain_descriptions) > 0), rain_descriptions


def send_discord_alert(message: str) -> None:
    """Discord Webhook 経由で通知を POST する。"""
    if not DISCORD_WEBHOOK_URL:
        return

    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    print("[Success] Discord alert dispatched.")


def send_telegram_alert(message: str) -> None:
    """Telegram Bot API 経由でメッセージを送信する。"""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return

    endpoint = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(endpoint, json=payload, timeout=10)
    response.raise_for_status()
    print("[Success] Telegram alert dispatched.")


def main() -> None:
    check_environment()

    try:
        is_raining, descriptions = will_it_rain()

        if is_raining:
            print(
                f"[Trigger] Rain detected in upcoming 12 hours: {', '.join(descriptions)}"
            )
            alert_message = (
                "🌧️ **雨天通知 / Rain Alert**\n"
                "今後12時間以内に雨（または雪）が降る予報です。傘を持って出かけてください！\n"
                f"詳細: {', '.join(descriptions)}"
            )

            if DISCORD_WEBHOOK_URL:
                send_discord_alert(alert_message)
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                send_telegram_alert(alert_message)
        else:
            print("[Skip] No rain forecast in the next 12 hours. Notification skipped.")

    except requests.exceptions.RequestException as e:
        print(f"[Network Error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
