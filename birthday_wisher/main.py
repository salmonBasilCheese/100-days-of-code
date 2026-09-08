import argparse
from datetime import datetime, timezone
from email.message import EmailMessage
import os
import random
import smtplib
import sys
import pandas as pd

BIRTHDAYS_FILE = "birthdays.csv"
QUOTES_FILE = "quotes.txt"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def load_quotes(filepath: str) -> list[str]:
    """名言テキストを読み込み、リストとして返す。"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"名言ファイル '{filepath}' が見つかりません。")
    with open(filepath, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    return quotes


def get_target_date() -> tuple[int, int]:
    """
    判定対象の月日 (month, day) を確定する。
    1. コマンドライン引数 --date MM-DD
    2. 環境変数 TARGET_DATE (MM-DD)
    3. 現在日 (UTC)
    """
    parser = argparse.ArgumentParser(description="Automated Birthday Wisher")
    parser.add_argument(
        "--date", type=str, help="Target date for testing in MM-DD format (e.g. 12-24)"
    )
    args, _ = parser.parse_known_args()

    target_date_str = args.date or os.environ.get("TARGET_DATE")

    if target_date_str:
        try:
            parts = target_date_str.strip().split("-")
            if len(parts) != 2:
                raise ValueError
            month = int(parts[0])
            day = int(parts[1])
            if not (1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError
            print(f"[Mode] Manual/Test date active: {month:02d}-{day:02d}")
            return month, day
        except ValueError:
            print(
                f"[Error] Invalid date format '{target_date_str}'. Please use MM-DD format (e.g. 12-24).",
                file=sys.stderr,
            )
            sys.exit(1)

    today = datetime.now(timezone.utc)
    return today.month, today.day


def send_birthday_email(
    sender_email: str, sender_password: str, recipient_email: str, name: str, quote: str
) -> None:
    """個別の対象者へ誕生日メールを送信する。"""
    msg = EmailMessage()
    msg["Subject"] = f"Happy Birthday, {name}!"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    body = (
        f"Dear {name},\n\n"
        "Happy Birthday! Wishing you an incredible year ahead filled with joy and success.\n\n"
        "Here is a quote for your special day:\n"
        f'"{quote}"\n\n'
        "Warm regards,\n"
        "Automated Birthday Wisher"
    )
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as connection:
        connection.starttls()
        connection.login(sender_email, sender_password)
        connection.send_message(msg)


def main() -> None:
    # 1. 判定対象日付の取得
    target_month, target_day = get_target_date()
    print(f"[Info] Checking birthdays for date: {target_month:02d}-{target_day:02d}")

    # 2. データ読み込み
    if not os.path.exists(BIRTHDAYS_FILE):
        print(f"[Error] Required file '{BIRTHDAYS_FILE}' not found.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(BIRTHDAYS_FILE)

    # うるう年対応: 2月28日判定時、平年であれば2月29日生まれの人も含める
    current_year = datetime.now(timezone.utc).year
    is_leap_year = (current_year % 4 == 0 and current_year % 100 != 0) or (
        current_year % 400 == 0
    )

    if target_month == 2 and target_day == 28 and not is_leap_year:
        matched_rows = df[(df["month"] == 2) & ((df["day"] == 28) | (df["day"] == 29))]
    else:
        matched_rows = df[(df["month"] == target_month) & (df["day"] == target_day)]

    # 3. ゼロ件境界防御: 該当者がいなければ早期安全終了
    if matched_rows.empty:
        print("[Info] No birthdays found for this date. Exiting cleanly.")
        return

    print(f"[Info] Found {len(matched_rows)} birthday(s) to process.")

    # 4. 認証情報の取得
    sender_email = os.environ.get("MY_EMAIL")
    sender_password = os.environ.get("MY_PASSWORD")

    if not sender_email or not sender_password:
        print(
            "[Error] Environment variables MY_EMAIL or MY_PASSWORD are not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 5. 名言データの読み込み
    try:
        quotes = load_quotes(QUOTES_FILE)
    except FileNotFoundError as e:
        print(f"[Error] {e}", file=sys.stderr)
        sys.exit(1)

    # 6. 送信ループ処理
    success_count = 0
    for _, row in matched_rows.iterrows():
        name = row["name"]
        recipient_email = row["email"]
        chosen_quote = random.choice(quotes)

        try:
            send_birthday_email(
                sender_email=sender_email,
                sender_password=sender_password,
                recipient_email=recipient_email,
                name=name,
                quote=chosen_quote,
            )
            print(f"[Success] Email sent to {name} <{recipient_email}>")
            success_count += 1
        except smtplib.SMTPAuthenticationError:
            print(
                "[Error] SMTP Authentication failed. Check your Gmail App Password.",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(
                f"[Error] Failed to send email to {name} <{recipient_email}>: {e}",
                file=sys.stderr,
            )

    print(
        f"[Summary] Completed: {success_count}/{len(matched_rows)} email(s) sent successfully."
    )


if __name__ == "__main__":
    main()
