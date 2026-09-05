import requests

# Open Trivia DB API エンドポイント
# amount=10: 10問取得
# type=boolean: True/False 形式に限定
URL = "https://opentdb.com/api.php?amount=10&category=22&difficulty=medium&type=boolean"


def fetch_question_data() -> list:
    """Open Trivia DB から問題データを取得し、辞書リストとして返す。"""
    try:
        response = requests.get(URL, timeout=10)
        # HTTPステータスコードが 200 番台でない場合に例外を送出
        response.raise_for_status()
        data = response.json()

        # APIレスポンスコードが 0（正常取得）であることを確認
        if data.get("response_code") == 0:
            return data.get("results", [])
        else:
            print(f"API Error: Response code {data.get('response_code')}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error occurred: {e}")
        return []


# main.py からの既存の参照形式（import question_data）を壊さないためのエクスポート
question_data = fetch_question_data()
