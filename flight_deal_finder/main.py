from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from data_manager import DataManager
from flight_search import FlightSearch
from notification_manager import NotificationManager

ORIGIN_IATA = os.environ.get("ORIGIN_IATA", "HND")


def validate_environment() -> None:
    required = [
        "SHEETY_ENDPOINT",
        "SHEETY_USERS_ENDPOINT",
        "SHEETY_TOKEN",
        "SERP_API_KEY",
    ]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        print(
            f"[Fatal] Missing required environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    validate_environment()

    data_manager = DataManager()
    flight_search = FlightSearch()
    notification_manager = NotificationManager()

    # 1. シートから目的地データと顧客リストを取得
    destinations = data_manager.get_destination_data()
    customers = data_manager.get_customer_emails()

    print(
        f"[*] Loaded {len(destinations)} destination(s) and {len(customers)} customer(s)."
    )
    if not destinations:
        print("[Exit] No destinations to search.")
        return

    tomorrow = datetime.now() + timedelta(days=1)
    six_months_later = datetime.now() + timedelta(days=180)

    # 2. 各目的地の最安値を検索・比較
    for row in destinations:
        city = row.get("city")
        iata_code = row.get("iataCode")
        lowest_price = row.get("lowestPrice")

        if not iata_code or lowest_price is None:
            continue

        target_price = int(lowest_price)
        print(
            f"[*] Checking flights to {city} ({iata_code}) | Target: JPY {target_price:,}..."
        )

        flight = flight_search.check_flights(
            origin_city_code=ORIGIN_IATA,
            destination_city_code=iata_code,
            from_time=tomorrow,
            to_time=six_months_later,
        )

        if not flight:
            continue

        flight_type = (
            "Direct"
            if flight.is_direct
            else f"Stopover ({flight.stops} via {flight.via_city})"
        )
        print(f"    -> Current: JPY {flight.price:,} ({flight.airline}, {flight_type})")

        # 3. 最安値ディール判定
        if flight.price < target_price:
            print(f"[DEAL DETECTED] JPY {flight.price:,} < JPY {target_price:,}!")
            notification_text = flight.format_notification_text(
                target_price=target_price
            )

            # Discord へ送信
            notification_manager.send_deal_alert(notification_text)

            # 顧客リストへ一斉送信
            if customers:
                print(f"[*] Dispatching deal emails to {len(customers)} customer(s)...")
                notification_manager.send_emails(
                    users=customers, message_body=notification_text
                )
        else:
            print(
                f"    -> No deal (JPY {flight.price:,} >= target JPY {target_price:,})."
            )


if __name__ == "__main__":
    main()
