import os
import sys
import requests


class DataManager:
    """Sheety API を介して Google スプレッドシートのデータを操作するクラス。"""

    def __init__(self) -> None:
        self.prices_endpoint = os.environ.get("SHEETY_ENDPOINT")
        self.users_endpoint = os.environ.get("SHEETY_USERS_ENDPOINT")
        self.token = os.environ.get("SHEETY_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get_destination_data(self) -> list[dict]:
        """目的地一覧を取得する。"""
        if not self.prices_endpoint or not self.token:
            print("[Fatal] Sheety prices configuration missing.", file=sys.stderr)
            sys.exit(1)

        try:
            response = requests.get(
                self.prices_endpoint, headers=self.headers, timeout=15
            )
            response.raise_for_status()
            data = response.json()
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return []
        except requests.exceptions.RequestException as e:
            print(f"[Error] Failed to fetch prices from Sheety: {e}", file=sys.stderr)
            return []

    def get_customer_emails(self) -> list[dict]:
        """Google フォーム連携の users シートから顧客名とメールアドレスを取得する。"""
        if not self.users_endpoint or not self.token:
            print("[Fatal] Sheety users configuration missing.", file=sys.stderr)
            sys.exit(1)

        try:
            response = requests.get(
                self.users_endpoint, headers=self.headers, timeout=15
            )
            response.raise_for_status()
            data = response.json()
            users_list = data.get("users", [])

            validated_users = []
            for user in users_list:
                first_name = user.get("whatIsYourFirstName?", "").strip()
                email = user.get("whatIsYourEmail?", "").strip()
                if email and "@" in email:
                    validated_users.append(
                        {
                            "first_name": first_name if first_name else "Valued Member",
                            "email": email,
                        }
                    )
            return validated_users

        except requests.exceptions.RequestException as e:
            print(f"[Error] Failed to fetch users from Sheety: {e}", file=sys.stderr)
            return []
