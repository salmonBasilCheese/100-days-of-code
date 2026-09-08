import requests

URL = "https://opentdb.com/api.php?amount=10&type=boolean"


def fetch_question_data() -> list[dict]:
    """Open Trivia DB から True/False 形式のクイズを10問取得する。"""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("response_code") == 0:
            return data.get("results", [])
        return []
    except requests.exceptions.RequestException as e:
        print(f"[Network Error] Could not fetch quiz data: {e}")
        return []


question_data = fetch_question_data()
