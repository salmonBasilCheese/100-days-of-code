from turtle import Turtle

SCORE_FONT = ("Courier", 40, "bold")
WINNER_FONT = ("Courier", 32, "bold")


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.l_score = 0
        self.r_score = 0
        self.draw_center_line()
        self.update_scoreboard()

    def draw_center_line(self) -> None:
        """画面中央 (x = 0) に破線を描画"""
        pen = Turtle()
        pen.hideturtle()
        pen.color("white")
        pen.pensize(2)
        pen.penup()
        pen.goto(0, 300)
        pen.setheading(270)

        # 300px から -300px まで 10px 刻みで描画
        for _ in range(30):
            pen.pendown()
            pen.forward(10)
            pen.penup()
            pen.forward(10)

    def update_scoreboard(self) -> None:
        """現在のスコアを描画"""
        self.clear()
        self.goto(-100, 200)
        self.write(self.l_score, align="center", font=SCORE_FONT)
        self.goto(100, 200)
        self.write(self.r_score, align="center", font=SCORE_FONT)

    def l_point(self) -> None:
        """Player 1 得点"""
        self.l_score += 1
        self.update_scoreboard()

    def r_point(self) -> None:
        """Player 2 得点"""
        self.r_score += 1
        self.update_scoreboard()

    def show_game_over(self, winner: str) -> None:
        """勝者告知画面の描画"""
        self.goto(0, 0)
        self.write(f"{winner} WINS!", align="center", font=WINNER_FONT)
