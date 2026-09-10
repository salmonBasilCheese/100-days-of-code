from dataclasses import dataclass


@dataclass(frozen=True)
class FlightData:
    """検索された航空券の確定情報を保持する不変データクラス。"""

    price: int
    origin_airport: str
    destination_airport: str
    outbound_date: str
    return_date: str
    airline: str
    is_direct: bool = True
    stops: int = 0
    via_city: str = ""

    def format_notification_text(self, target_price: int) -> str:
        """Discord および メール本文用の通知テキストを生成する。"""
        savings = target_price - self.price
        msg = (
            f"Low Flight Price Alert!\n"
            f"Route: {self.origin_airport} -> {self.destination_airport}\n"
            f"Price: JPY {self.price:,} (Target: JPY {target_price:,} | Save: JPY {savings:,})\n"
            f"Dates: {self.outbound_date} to {self.return_date}\n"
            f"Airline: {self.airline}\n"
        )
        if not self.is_direct:
            msg += f"Flight has {self.stops} stopover, via {self.via_city}."
        return msg
