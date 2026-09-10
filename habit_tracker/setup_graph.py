from pathlib import Path
import os
import sys
import time
from dotenv import load_dotenv
import requests

# 同階層の .env をロード
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

PIXELA_USERNAME = os.environ.get("PIXELA_USERNAME")
PIXELA_TOKEN = os.environ.get("PIXELA_TOKEN")
PIXELA_GRAPH_ID = os.environ.get("PIXELA_GRAPH_ID", "graph1")

PIXELA_ENDPOINT = "https://pixe.la/v1/users"


def validate_config() -> None:
    """設定値の存在と命名制約を検証する。"""
    if not PIXELA_USERNAME or not PIXELA_TOKEN:
        print("[Fatal] PIXELA_USERNAME and PIXELA_TOKEN must be set in .env", file=sys.stderr)
        sys.exit(1)
    if not PIXELA_USERNAME.islower() or not PIXELA_USERNAME.replace("-", "").isalnum():
        print("[Fatal] PIXELA_USERNAME must be lowercase alphanumeric and hyphens only [a-z0-9-].", file=sys.stderr)
        sys.exit(1)


def send_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """Pixela 固有の確率的エラー (503 / isSuccess: false) に対するリトライ付き通信ラッパー。"""
    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            # 200〜299 または特定ステータス以外の通信エラーは raise
            if response.status_code in [200, 201]:
                data = response.json()
                if data.get("isSuccess", False):
                    return response
                print(f"[Retry {attempt}/{max_retries}] API responded with isSuccess=False: {data.get('message')}")
            elif response.status_code in [409]:
                # 既に作成済みの競合はそのまま返す
                return response
            elif response.status_code in [503, 500]:
                print(f"[Retry {attempt}/{max_retries}] Pixela Server busy (HTTP {response.status_code})")
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[Retry {attempt}/{max_retries}] Network exception: {e}")

        if attempt < max_retries:
            sleep_sec = 2 ** (attempt - 1)
            time.sleep(sleep_sec)

    print("[Fatal] Exceeded maximum retry attempts.", file=sys.stderr)
    sys.exit(1)


def create_user() -> None:
    """Pixela ユーザーアカウントを作成する。"""
    user_params = {
        "token": PIXELA_TOKEN,
        "username": PIXELA_USERNAME,
        "agreeTermsOfService": "yes",
        "notMinor": "yes",
    }
    print(f"[*] Attempting to create user: {PIXELA_USERNAME}...")
    res = send_with_retry("POST", PIXELA_ENDPOINT, json=user_params)
    res_data = res.json()
    if res.status_code == 409 or "already exists" in res_data.get("message", ""):
        print(f"[Skip] User '{PIXELA_USERNAME}' already exists.")
    else:
        print(f"[Success] User created: {res_data.get('message')}")


def create_graph() -> None:
    """Pixela グラフ定義を作成する。"""
    graph_endpoint = f"{PIXELA_ENDPOINT}/{PIXELA_USERNAME}/graphs"
    headers = {"X-USER-TOKEN": PIXELA_TOKEN}
    graph_config = {
        "id": PIXELA_GRAPH_ID,
        "name": "Coding Tracker",
        "unit": "Hours",
        "type": "float",
        "color": "shibafu",  # 緑系統
        "timezone": "Asia/Tokyo",
    }
    print(f"[*] Attempting to create graph: {PIXELA_GRAPH_ID}...")
    res = send_with_retry("POST", graph_endpoint, json=graph_config, headers=headers)
    res_data = res.json()
    if res.status_code == 409 or "already exists" in res_data.get("message", ""):
        print(f"[Skip] Graph '{PIXELA_GRAPH_ID}' already exists.")
    else:
        print(f"[Success] Graph created: {res_data.get('message')}")
        print(f"[*] View your graph at: https://pixe.la/v1/users/{PIXELA_USERNAME}/graphs/{PIXELA_GRAPH_ID}.html")


if __name__ == "__main__":
    validate_config()
    create_user()
    create_graph()