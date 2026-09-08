import os
import time
import tkinter as tk
import turtle
import pandas as pd

# 定数定義
CSV_FILE = "50_states.csv"
IMAGE_FILE = "blank_states_img.gif"
OUTPUT_CSV = "states_to_learn.csv"
TOTAL_STATES = 50
TIME_LIMIT_SECONDS = 600  # 10分 (Sporcle仕様)
SCREEN_WIDTH = 725
SCREEN_HEIGHT = 491


def format_time(seconds: float) -> str:
    """秒数を mm:ss 形式の文字列に変換"""
    clamped_sec = max(0, int(seconds))
    mins = clamped_sec // 60
    secs = clamped_sec % 60
    return f"{mins:02d}:{secs:02d}"


def export_missing_states(all_states: list[str], guessed_states: list[str]) -> None:
    """未正解の州を抽出して states_to_learn.csv へ出力"""
    missing_states = [state for state in all_states if state not in guessed_states]
    if missing_states:
        df_missing = pd.DataFrame(missing_states, columns=["state"])
        df_missing.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
        print(
            f"\n[Info] {len(missing_states)} missing states exported to '{OUTPUT_CSV}'."
        )


def main() -> None:
    # 1. 依存ファイルの存在確認
    if not os.path.exists(CSV_FILE) or not os.path.exists(IMAGE_FILE):
        print(f"[Error] Required files ('{CSV_FILE}' or '{IMAGE_FILE}') are missing.")
        return

    # 2. データ読み込み (Pandas)
    df = pd.read_csv(CSV_FILE)
    all_states: list[str] = df["state"].to_list()
    guessed_states: list[str] = []

    # 3. 画面および背景設定
    screen = turtle.Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.title("U.S. States Quiz")
    screen.addshape(IMAGE_FILE)

    bg_turtle = turtle.Turtle()
    bg_turtle.shape(IMAGE_FILE)

    # 4. 州名描画用 Turtle
    writer = turtle.Turtle()
    writer.hideturtle()
    writer.penup()
    writer.color("black")
    writer.speed("fastest")

    # 5. タイマー開始
    start_time = time.time()

    # 6. クイズメインループ
    try:
        while len(guessed_states) < TOTAL_STATES:
            # 経過時間および残り時間の計算 (タイムスタンプ差分方式)
            elapsed_time = time.time() - start_time
            remaining_time = TIME_LIMIT_SECONDS - elapsed_time

            # 制限時間切れ判定
            if remaining_time <= 0:
                writer.teleport(0, 0)
                writer.color("red")
                writer.write("TIME'S UP!", align="center", font=("Arial", 24, "bold"))
                export_missing_states(all_states, guessed_states)
                time.sleep(2)
                break

            time_str = format_time(remaining_time)
            score_title = (
                f"{len(guessed_states)}/{TOTAL_STATES} States | Time: {time_str}"
            )

            # モーダルダイアログによる回答取得
            answer_raw = screen.textinput(
                title=score_title,
                prompt="What's another state's name? (Type 'Exit' to quit)",
            )

            # キャンセルボタン押下 または "Exit" 入力によるギブアップ終了
            if answer_raw is None:
                export_missing_states(all_states, guessed_states)
                break

            answer_state = answer_raw.strip().title()

            if answer_state in ["Exit", "Quit"]:
                export_missing_states(all_states, guessed_states)
                break

            # 入力完了後の時間再チェック（入力中に時間切れになった場合の防衛）
            if time.time() - start_time >= TIME_LIMIT_SECONDS:
                writer.teleport(0, 0)
                writer.color("red")
                writer.write("TIME'S UP!", align="center", font=("Arial", 24, "bold"))
                export_missing_states(all_states, guessed_states)
                time.sleep(2)
                break

            # 正解判定および未回答チェック（重複回答の防御）
            if answer_state in all_states and answer_state not in guessed_states:
                guessed_states.append(answer_state)

                # Pandas による座標抽出 (型安全なスカラー値変換)
                state_row = df[df["state"] == answer_state]
                target_x = int(state_row["x"].iloc[0])
                target_y = int(state_row["y"].iloc[0])

                # 地図上への州名テキスト描画
                writer.color("black")
                writer.teleport(target_x, target_y)
                writer.write(answer_state, align="center", font=("Arial", 8, "normal"))

        # 全問正解クリア判定
        if len(guessed_states) == TOTAL_STATES:
            writer.teleport(0, 0)
            writer.color("blue")
            writer.write("YOU WIN! 50/50!", align="center", font=("Arial", 24, "bold"))
            time.sleep(3)

        screen.exitonclick()

    except (turtle.Terminator, tk.TclError):
        # 画面の「×」閉じによる安全終了時も学習用データを確実に保存
        export_missing_states(all_states, guessed_states)


if __name__ == "__main__":
    main()
