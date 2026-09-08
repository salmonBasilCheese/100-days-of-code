import math
import os
import tkinter as tk

# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

# 状態管理変数
reps = 0
timer = None
is_running = False


# ---------------------------- TIMER RESET ------------------------------- #
def reset_timer():
    """
    リセット処理:
    - 稼働中タイマーの破棄 (after_cancel)
    - 状態変数 (reps, timer, is_running) のアトミック初期化
    - UI表示 (タイトル, 時間, チェックマーク) の初期化
    """
    global reps, timer, is_running

    if timer is not None:
        window.after_cancel(timer)
        timer = None

    reps = 0
    is_running = False

    canvas.itemconfig(timer_text, text="00:00")
    title_label.config(text="Timer", fg=GREEN)
    check_marks.config(text="")


# ---------------------------- TIMER MECHANISM ------------------------------- #
def start_timer():
    """
    タイマー開始処理:
    - 多重起動インターロック (is_running == True 時は無視)
    - reps に基づくセッション種別の判定 (Work / Short Break / Long Break)
    """
    global reps, is_running

    # 多重タイマー起動の防御
    if is_running:
        return

    is_running = True
    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps % 8 == 0:
        count_down(long_break_sec)
        title_label.config(text="Break", fg=RED)
    elif reps % 2 == 0:
        count_down(short_break_sec)
        title_label.config(text="Break", fg=PINK)
    else:
        count_down(work_sec)
        title_label.config(text="Work", fg=GREEN)


# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #
def count_down(count):
    """
    カウントダウン非同期ループ:
    - ゼロ埋めフォーマット (mm:ss) によるテキスト更新
    - window.after() による1秒ごとの非同期再帰
    - 0秒到達時のセッション切り替え・最前面通知・チェックマーク加算
    """
    global timer, is_running

    count_min = count // 60
    count_sec = count % 60

    # 2桁ゼロ埋めフォーマット
    canvas.itemconfig(timer_text, text=f"{count_min:02d}:{count_sec:02d}")

    if count > 0:
        timer = window.after(1000, count_down, count - 1)
    else:
        # 0秒到達時: 稼働フラグを一旦解除して次セッションを開始
        is_running = False
        start_timer()

        # チェックマーク更新: 作業(Work)完了回数 = floor(reps / 2)
        work_sessions = math.floor(reps / 2)
        marks = "✔" * work_sessions
        check_marks.config(text=marks)

        # ウィンドウの最前面ポップアップ通知
        window.attributes("-topmost", 1)
        window.attributes("-topmost", 0)


# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title("Pomodoro")
window.config(padx=100, pady=50, bg=YELLOW)

# 1. タイトルラベル (行0, 列1)
title_label = tk.Label(text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 50, "bold"))
title_label.grid(column=1, row=0)

# 2. Canvas & トマト画像 & タイマー文字列 (行1, 列1)
canvas = tk.Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
image_path = "tomato.png"
if os.path.exists(image_path):
    tomato_img = tk.PhotoImage(file=image_path)
    canvas.create_image(100, 112, image=tomato_img)
else:
    # 画像ファイル不在時の安全フォールバック
    canvas.create_oval(10, 20, 190, 200, fill="red", outline="")

timer_text = canvas.create_text(
    100, 130, text="00:00", fill="white", font=(FONT_NAME, 35, "bold")
)
canvas.grid(column=1, row=1)

# 3. Start ボタン (行2, 列0)
start_button = tk.Button(
    text="Start",
    highlightthickness=0,
    font=(FONT_NAME, 10, "bold"),
    command=start_timer,
)
start_button.grid(column=0, row=2)

# 4. Reset ボタン (行2, 列2)
reset_button = tk.Button(
    text="Reset",
    highlightthickness=0,
    font=(FONT_NAME, 10, "bold"),
    command=reset_timer,
)
reset_button.grid(column=2, row=2)

# 5. チェックマークラベル (行3, 列1)
check_marks = tk.Label(fg=GREEN, bg=YELLOW, font=("Arial", 16, "bold"))
check_marks.grid(column=1, row=3)

if __name__ == "__main__":
    window.mainloop()
