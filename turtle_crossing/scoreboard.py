from turtle import Turtle

SCORE_FONT = ("Courier", 18, "bold")
GAME_OVER_FONT = ("Courier", 24, "bold")
SUB_FONT = ("Courier", 14, "normal")
HEADER_POSITION = (-280, 260)


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.hideturtle()
        self.penup()
        self.color("black")
        self.goto(HEADER_POSITION)
        self.update_scoreboard()

    def update_scoreboard(self) -> None:
        """現在レベルの描画"""
        self.clear()
        self.goto(HEADER_POSITION)
        self.write(f"Level: {self.level}", align="left", font=SCORE_FONT)

    def increase_level(self) -> None:
        """レベル加算と再描画"""
        self.level += 1
        self.update_scoreboard()

    def game_over(self) -> None:
        """ゲームオーバーおよびリトライ操作の案内描画"""
        self.goto(0, 20)
        self.write("GAME OVER", align="center", font=GAME_OVER_FONT)
        self.goto(0, -20)
        self.write("Press SPACE to Restart", align="center", font=SUB_FONT)

    def reset(self) -> None:
        """スコアのリセット"""
        self.level = 1
        self.update_scoreboard()
