import os

# 観測地点の座標 (デフォルト: ロンドン / 必要に応じて自身の緯度・経度に変更)
MY_LAT = float(os.environ.get("MY_LAT", 33.525441))
MY_LONG = float(os.environ.get("MY_LONG", 133.608107))

# メール通知設定
MY_EMAIL = os.environ.get("MY_EMAIL", "pishiki.hosokawa@gmail.com")
MY_PASSWORD = os.environ.get("MY_PASSWORD", "ijexdqedzwrerhqj")
TO_EMAIL = os.environ.get("TO_EMAIL", MY_EMAIL)
