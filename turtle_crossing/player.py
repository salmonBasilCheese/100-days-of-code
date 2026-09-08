from turtle import Turtle

STARTING_POSITION = (0, -280)
MOVE_DISTANCE = 10
FINISH_LINE_Y = 280


class Player(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.color("black")
        self.penup()
        self.setheading(90)  # 北（上向き）固定
        self.go_to_start()

    def go_up(self) -> None:
        """上方向（北）へ前進。仕様として後退・左右移動は排除"""
        self.forward(MOVE_DISTANCE)

    def go_to_start(self) -> None:
        """初期スポーン位置へリセット"""
        self.goto(STARTING_POSITION)

    def is_at_finish_line(self) -> bool:
        """ゴール境界判定 (y >= 280)"""
        return self.ycor() >= FINISH_LINE_Y
