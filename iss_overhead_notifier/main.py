import argparse
from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib
import sys
import time
import requests

from config import MY_LAT, MY_LONG, MY_EMAIL, MY_PASSWORD, TO_EMAIL

ISS_API_URL = "http://api.open-notify.org/iss-now.json"
SUNRISE_SUNSET_API_URL = "https://api.sunrise-sunset.org/json"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def is_iss_overhead() -> tuple[bool, float, float]:
    """
    ISS の現在位置を取得し、現在地から ±5 度以内に接近しているか判定する。
    戻り値: (接近判定フラグ, iss_lat, iss_long)
    """
    response = requests.get(ISS_API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    iss_lat = float(data["iss_position"]["latitude"])
    iss_long = float(data["iss_position"]["longitude"])

    is_near = (abs(MY_LAT - iss_lat) <= 5) and (abs(MY_LONG - iss_long) <= 5)
    return is_near, iss_lat, iss_long


def is_night() -> bool:
    """
    日の出・日の入り時刻 API を取得し、現在時刻 (UTC) が日没後または日の出前 (夜間) か判定する。
    """
    params = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }
    response = requests.get(SUNRISE_SUNSET_API_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # ISO 8601 文字列から時 (UTC) を抽出
    sunrise_hour = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset_hour = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    current_hour = datetime.now(timezone.utc).hour

    # 夜間判定: 日没後 または 日の出前
    return current_hour >= sunset_hour or current_hour <= sunrise_hour


def send_notification(iss_lat: float, iss_long: float) -> None:
    """観測可能通知メールを送信する。"""
    if not MY_EMAIL or not MY_PASSWORD or "your_app_password" in MY_PASSWORD:
        print("[Error] Email credentials are not configured properly.", file=sys.stderr)
        return

    msg = EmailMessage()
    msg["Subject"] = "Look Up! 👆 (ISS is Overhead)"
    msg["From"] = MY_EMAIL
    msg["To"] = TO_EMAIL

    body = (
        "The International Space Station (ISS) is currently above your location!\n\n"
        f"Your Location: Lat {MY_LAT}, Long {MY_LONG}\n"
        f"ISS Current Position: Lat {iss_lat}, Long {iss_long}\n\n"
        "Go outside and look up at the night sky!"
    )
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.send_message(msg)
    print(f"[Success] Notification sent to {TO_EMAIL}")


def check_and_notify() -> None:
    """接近判定と夜間判定を実行し、条件成立時のみメールを送信する。"""
    try:
        is_near, iss_lat, iss_long = is_iss_overhead()
        night_time = is_night()

        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"ISS: ({iss_lat:.2f}, {iss_long:.2f}) | Near: {is_near} | Night: {night_time}"
        )

        if is_near and night_time:
            print("[Trigger] ISS is overhead and it is dark! Sending email...")
            send_notification(iss_lat, iss_long)
        else:
            reason = []
            if not is_near:
                reason.append("ISS is not within ±5 degrees")
            if not night_time:
                reason.append("It is daytime")
            print(f"[Skip] {', '.join(reason)}.")

    except requests.exceptions.RequestException as e:
        print(f"[Network Error] {e}", file=sys.stderr)
    except Exception as e:
        print(f"[Unexpected Error] {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="ISS Overhead Notifier")
    parser.add_argument(
        "--once", action="store_true", help="Run once and exit (for cron/CI)"
    )
    args = parser.parse_args()

    if args.once:
        check_and_notify()
    else:
        print(
            "[Info] Starting ISS tracking daemon (interval: 60s). Press Ctrl+C to stop."
        )
        while True:
            check_and_notify()
            time.sleep(60)


if __name__ == "__main__":
    main()
