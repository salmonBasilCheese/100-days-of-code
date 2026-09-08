from turtle import Turtle

PADDLE_WIDTH_STRETCH = 5  # 高さ 100px (20px * 5)
PADDLE_LEN_STRETCH = 1  # 幅 20px (20px * 1)
MOVE_STEP = 20
Y_LIMIT = 250  # 上下端クランプ境界 (300 - 50)


class Paddle(Turtle):
    def __init__(self, position: tuple[int, int]):
        super().__init__()
        self.shape("square")
        self.color("white")
        self.shapesize(stretch_wid=PADDLE_WIDTH_STRETCH, stretch_len=PADDLE_LEN_STRETCH)
        self.penup()
        self.goto(position)

    def up(self) -> None:
        """上限境界 (250px) を超えない範囲でパドルを上方向へ移動"""
        if self.ycor() < Y_LIMIT:
            new_y = min(self.ycor() + MOVE_STEP, Y_LIMIT)
            self.sety(new_y)

    def down(self) -> None:
        """下限境界 (-250px) を超えない範囲でパドルを下方向へ移動"""
        if self.ycor() > -Y_LIMIT:
            new_y = max(self.ycor() - MOVE_STEP, -Y_LIMIT)
            self.sety(new_y)
