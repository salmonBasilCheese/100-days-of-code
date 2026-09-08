import os
import sys
from tkinter import Tk, Canvas, PhotoImage, Button
import requests

API_URL = "https://api.kanye.rest"


def get_quote() -> None:
    """
    Kanye.rest API から引用文を取得し、Canvas のテキストを更新する。
    ネットワーク例外、タイムアウト、テキスト長境界をハンドリングする。
    """
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        quote: str = data["quote"]
    except requests.exceptions.Timeout:
        quote = "Request timed out. Try again."
    except requests.exceptions.RequestException:
        quote = "Failed to fetch quote. Check your network."
    except (KeyError, ValueError):
        quote = "Invalid response from server."

    # 文字長に応じた動的フォントスケーリング（枠外はみ出し防御）
    font_size = 18 if len(quote) > 100 else 24
    canvas.itemconfig(quote_text, text=quote, font=("Arial", font_size, "bold"))


# ---------------------------- UI SETUP ------------------------------- #
window = Tk()
window.title("Kanye Says...")
window.config(padx=50, pady=50)

# アセット存在確認
for asset in ["background.png", "kanye.png"]:
    if not os.path.exists(asset):
        print(f"[Error] Required asset '{asset}' not found.", file=sys.stderr)
        sys.exit(1)

# Canvas (吹き出し & 引用文テキスト)
canvas = Canvas(width=300, height=414, highlightthickness=0)
background_img = PhotoImage(file="background.png")
canvas.create_image(150, 207, image=background_img)
quote_text = canvas.create_text(
    150,
    207,
    text="Loading quote...",
    width=250,
    font=("Arial", 24, "bold"),
    fill="white",
)
canvas.grid(row=0, column=0)

# Kanye ボタン
kanye_img = PhotoImage(file="kanye.png")
kanye_button = Button(
    image=kanye_img,
    highlightthickness=0,
    bd=0,
    command=get_quote,
)
kanye_button.grid(row=1, column=0)

# 起動時の初期ロード
get_quote()

if __name__ == "__main__":
    window.mainloop()
