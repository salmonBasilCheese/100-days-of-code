import os
import random
import tkinter as tk
from tkinter import messagebox
import pandas as pd

BACKGROUND_COLOR = "#B1DDC6"
DATA_TO_LEARN = "data/words_to_learn.csv"
DATA_ORIGINAL = "data/french_words.csv"
# ルート直下に配置されている場合のフォールバックパス
DATA_ORIGINAL_FALLBACK = "french_words.csv"

# 状態管理変数
to_learn: list[dict[str, str]] = []
current_card: dict[str, str] = {}
flip_timer = None


# ---------------------------- DATA LOADING ------------------------------- #
def load_words() -> list[dict[str, str]]:
    """学習用単語データを読み込み、辞書のリストとして返す。"""
    try:
        df = pd.read_csv(DATA_TO_LEARN)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        target_path = (
            DATA_ORIGINAL if os.path.exists(DATA_ORIGINAL) else DATA_ORIGINAL_FALLBACK
        )
        if not os.path.exists(target_path):
            messagebox.showerror(
                "Error", f"マスターデータ '{target_path}' が見つかりません。"
            )
            return []
        df = pd.read_csv(target_path)

    return df.to_dict(orient="records")


# ---------------------------- CARD MECHANISM ------------------------------- #
def next_card():
    """表面（フランス語）を表示し、3秒後に裏返す非同期タイマーをセットする。"""
    global current_card, flip_timer

    # 1. 既存タイマーの破棄（連打による暴発を防止）
    if flip_timer is not None:
        window.after_cancel(flip_timer)

    # 2. リスト枯渇（全単語習得）時の境界ガード
    if not to_learn:
        canvas.itemconfig(card_bg, image=card_front_img)
        canvas.itemconfig(card_title, text="Congratulations!", fill="black")
        canvas.itemconfig(card_word, text="All words learned!", fill="black")
        right_button.config(state="disabled")
        wrong_button.config(state="disabled")
        return

    # 3. 新しいカードの選定と表面描画
    current_card = random.choice(to_learn)
    canvas.itemconfig(card_bg, image=card_front_img)
    canvas.itemconfig(card_title, text="French", fill="black")
    canvas.itemconfig(card_word, text=current_card["French"], fill="black")

    # 4. 3秒後の自動フリップを予約
    flip_timer = window.after(3000, func=flip_card)


def flip_card():
    """裏面（英語対訳）を表示する。"""
    canvas.itemconfig(card_bg, image=card_back_img)
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card["English"], fill="white")


def is_known():
    """正解（✔）処理: 現在の単語をリストから除外し、CSVへ保存して次へ進む。"""
    global to_learn
    if current_card in to_learn:
        to_learn.remove(current_card)
        # フォルダの存在を保証して保存
        os.makedirs(os.path.dirname(DATA_TO_LEARN), exist_ok=True)
        df = pd.DataFrame(to_learn)
        df.to_csv(DATA_TO_LEARN, index=False, encoding="utf-8")

    next_card()


# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)


# アセット画像の安全なロード関数
def get_image_path(filename: str) -> str:
    sub_path = os.path.join("images", filename)
    return sub_path if os.path.exists(sub_path) else filename


card_front_img = tk.PhotoImage(file=get_image_path("card_front.png"))
card_back_img = tk.PhotoImage(file=get_image_path("card_back.png"))
right_img = tk.PhotoImage(file=get_image_path("right.png"))
wrong_img = tk.PhotoImage(file=get_image_path("wrong.png"))

# 1. Canvas (カード背景 & テキスト)
canvas = tk.Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
card_bg = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 150, text="", font=("Arial", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Arial", 60, "bold"))
canvas.grid(row=0, column=0, columnspan=2)

# 2. 不正解ボタン (✖: 単語を残して次へ)
wrong_button = tk.Button(
    image=wrong_img,
    highlightthickness=0,
    bd=0,
    bg=BACKGROUND_COLOR,
    activebackground=BACKGROUND_COLOR,
    command=next_card,
)
wrong_button.grid(row=1, column=0)

# 3. 正解ボタン (✔: 単語をリストから削除・保存して次へ)
right_button = tk.Button(
    image=right_img,
    highlightthickness=0,
    bd=0,
    bg=BACKGROUND_COLOR,
    activebackground=BACKGROUND_COLOR,
    command=is_known,
)
right_button.grid(row=1, column=1)

# データの読み込みと初回復旧
to_learn = load_words()
next_card()

if __name__ == "__main__":
    window.mainloop()
