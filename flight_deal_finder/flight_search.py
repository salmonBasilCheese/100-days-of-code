from datetime import datetime, timedelta
import os
import sys
import requests_cache
from flight_data import FlightData


class FlightSearch:
    """SerpAPI Google Flights API を操作するクラス。"""

    def __init__(self) -> None:
        self.api_key = os.environ.get("SERP_API_KEY")
        self.endpoint = "https://serpapi.com/search"

        self.session = requests_cache.CachedSession(
            "serpapi_cache",
            expire_after=timedelta(hours=12),
            allowable_methods=["GET"],
        )

    def check_flights(
        self,
        origin_city_code: str,
        destination_city_code: str,
        from_time: datetime,
        to_time: datetime,
    ) -> FlightData | None:
        """直行便、または経由便を検索して最安値データを構築する。"""
        if not self.api_key:
            print("[Fatal] SERP_API_KEY is not configured.", file=sys.stderr)
            sys.exit(1)

        outbound_date_str = from_time.strftime("%Y-%m-%d")
        return_date_str = (from_time + timedelta(days=7)).strftime("%Y-%m-%d")

        params = {
            "engine": "google_flights",
            "departure_id": origin_city_code,
            "arrival_id": destination_city_code,
            "outbound_date": outbound_date_str,
            "return_date": return_date_str,
            "currency": "JPY",
            "hl": "en",
            "api_key": self.api_key,
        }

        try:
            response = self.session.get(self.endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            flights_list = data.get("best_flights") or data.get("other_flights")
            if not flights_list:
                print(
                    f"[Info] No flights available for {origin_city_code} -> {destination_city_code}"
                )
                return None

            cheapest_flight = flights_list[0]
            price = cheapest_flight.get("price")
            if price is None:
                return None

            flight_legs = cheapest_flight.get("flights", [])
            airline = (
                flight_legs[0].get("airline", "Unknown Airline")
                if flight_legs
                else "Unknown Airline"
            )

            # レグ数（区間数）から直行便か経由便かを判定
            is_direct = len(flight_legs) == 1
            stops = len(flight_legs) - 1
            via_city = (
                flight_legs[0].get("arrival_airport", {}).get("name", "")
                if not is_direct
                else ""
            )

            return FlightData(
                price=int(price),
                origin_airport=origin_city_code,
                destination_airport=destination_city_code,
                outbound_date=outbound_date_str,
                return_date=return_date_str,
                airline=airline,
                is_direct=is_direct,
                stops=stops,
                via_city=via_city,
            )

        except requests_cache.exceptions.RequestException as e:
            print(
                f"[Error] SerpAPI request failed for {destination_city_code}: {e}",
                file=sys.stderr,
            )
            return None
