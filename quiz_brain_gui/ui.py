import os
import sys
from tkinter import Tk, Canvas, Label, Button, PhotoImage
from quiz_brain import QuizBrain

THEME_COLOR = "#375362"


class QuizInterface:
    def __init__(self, quiz_brain: QuizBrain):
        self.quiz = quiz_brain

        # ウィンドウ初期化
        self.window = Tk()
        self.window.title("Quizzler")
        self.window.config(padx=20, pady=20, bg=THEME_COLOR)

        # 1. スコアラベル (行0, 列1)
        self.score_label = Label(
            text="Score: 0",
            fg="white",
            bg=THEME_COLOR,
            font=("Arial", 12, "bold"),
        )
        self.score_label.grid(row=0, column=1)

        # 2. 問題表示用 Canvas (行1, 列0-1)
        self.canvas = Canvas(width=300, height=250, bg="white", highlightthickness=0)
        self.question_text = self.canvas.create_text(
            150,
            125,
            width=280,
            text="Loading question...",
            fill=THEME_COLOR,
            font=("Arial", 18, "italic"),
        )
        self.canvas.grid(row=1, column=0, columnspan=2, pady=50)

        # アセット画像の安全なロード
        true_img_path = self._resolve_asset_path("true.png")
        false_img_path = self._resolve_asset_path("false.png")

        self.true_image = PhotoImage(file=true_img_path)
        self.false_image = PhotoImage(file=false_img_path)

        # 3. True ボタン (行2, 列0)
        self.true_button = Button(
            image=self.true_image,
            highlightthickness=0,
            bd=0,
            bg=THEME_COLOR,
            activebackground=THEME_COLOR,
            command=self.true_pressed,
        )
        self.true_button.grid(row=2, column=0)

        # 4. False ボタン (行2, 列1)
        self.false_button = Button(
            image=self.false_image,
            highlightthickness=0,
            bd=0,
            bg=THEME_COLOR,
            activebackground=THEME_COLOR,
            command=self.false_pressed,
        )
        self.false_button.grid(row=2, column=1)

        # 初期問題の出題
        self.get_next_question()

        self.window.mainloop()

    def _resolve_asset_path(self, filename: str) -> str:
        """images フォルダ内または直下から画像パスを解決する。"""
        sub_path = os.path.join("images", filename)
        if os.path.exists(sub_path):
            return sub_path
        if os.path.exists(filename):
            return filename
        print(
            f"[Error] Required asset '{filename}' not found in 'images/' or root.",
            file=sys.stderr,
        )
        sys.exit(1)

    def get_next_question(self) -> None:
        """次問を描画、または終了画面へ移行する。"""
        # Canvas背景色をリセット
        self.canvas.config(bg="white")

        if self.quiz.still_has_questions():
            self.score_label.config(text=f"Score: {self.quiz.score}")
            q_text = self.quiz.next_question()
            self.canvas.itemconfig(self.question_text, text=q_text)
            # ボタンを有効化（フィードバック待機後の復帰）
            self.true_button.config(state="normal")
            self.false_button.config(state="normal")
        else:
            # 終了境界処理: リスト枯渇
            final_message = f"You've reached the end of the quiz.\n\nFinal Score: {self.quiz.score}/{len(self.quiz.question_list)}"
            self.canvas.itemconfig(self.question_text, text=final_message)
            self.score_label.config(text=f"Score: {self.quiz.score}")
            self.true_button.config(state="disabled")
            self.false_button.config(state="disabled")

    def true_pressed(self) -> None:
        """True押下時のイベントハンドラ"""
        is_right = self.quiz.check_answer("True")
        self.give_feedback(is_right)

    def false_pressed(self) -> None:
        """False押下時のイベントハンドラ"""
        is_right = self.quiz.check_answer("False")
        self.give_feedback(is_right)

    def give_feedback(self, is_right: bool) -> None:
        """
        回答判定に応じた背景色変更と、連打防止インターロック。
        1秒後に get_next_question を非同期実行する。
        """
        # 連打・多重加算防止のためボタンを無効化
        self.true_button.config(state="disabled")
        self.false_button.config(state="disabled")

        if is_right:
            self.canvas.config(bg="green")
        else:
            self.canvas.config(bg="red")

        # 1000ミリ秒（1秒）後に次問へ進む
        self.window.after(1000, self.get_next_question)
