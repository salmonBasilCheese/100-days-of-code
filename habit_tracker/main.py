from datetime import datetime
from pathlib import Path
import os
import sys
import time
from dotenv import load_dotenv
import requests

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

PIXELA_USERNAME = os.environ.get("PIXELA_USERNAME")
PIXELA_TOKEN = os.environ.get("PIXELA_TOKEN")
PIXELA_GRAPH_ID = os.environ.get("PIXELA_GRAPH_ID", "graph1")
DEFAULT_QUANTITY = os.environ.get("DEFAULT_QUANTITY", "1.0")

BASE_URL = "https://pixe.la/v1/users"


def validate_environment() -> None:
    """必須環境変数の存在を検証する。"""
    missing = []
    if not PIXELA_USERNAME:
        missing.append("PIXELA_USERNAME")
    if not PIXELA_TOKEN:
        missing.append("PIXELA_TOKEN")

    if missing:
        print(
            f"[Fatal] Missing required environment variables: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)


def send_pixel_with_retry(date_str: str, quantity: str) -> None:
    """
    指定日にピクセルを打刻する。
    Pixela API の確率的リトライ制限 (503, isSuccess: false) に備え、指数バックオフで再試行を行う。
    """
    endpoint = f"{BASE_URL}/{PIXELA_USERNAME}/graphs/{PIXELA_GRAPH_ID}"
    headers = {"X-USER-TOKEN": PIXELA_TOKEN}
    payload = {
        "date": date_str,
        "quantity": str(quantity),
    }

    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"[*] Dispatching pixel [{date_str}: {quantity}] (Attempt {attempt}/{max_retries})..."
            )
            response = requests.post(
                endpoint, json=payload, headers=headers, timeout=10
            )

            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("isSuccess", False):
                    print(
                        f"[Success] Pixel recorded successfully: {data.get('message')}"
                    )
                    print(
                        f"[*] Dashboard: https://pixe.la/v1/users/{PIXELA_USERNAME}/graphs/{PIXELA_GRAPH_ID}.html"
                    )
                    return
                print(f"[Retry] API returned isSuccess=False: {data.get('message')}")
            elif response.status_code in [503, 500]:
                print(f"[Retry] Server busy (HTTP {response.status_code})")
            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"[Retry] Network/HTTP Exception: {e}")

        if attempt < max_retries:
            backoff_sec = 2 ** (attempt - 1)
            print(f"[*] Waiting {backoff_sec}s before next retry...")
            time.sleep(backoff_sec)

    print(
        f"[Fatal] Failed to record pixel for {date_str} after {max_retries} attempts.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    validate_environment()

    # 厳密な yyyyMMdd 形式で本日の日付を取得
    target_date = datetime.now().strftime("%Y%m%d")
    quantity = DEFAULT_QUANTITY

    send_pixel_with_retry(date_str=target_date, quantity=quantity)


if __name__ == "__main__":
    main()
