import turtle
from turtle import Screen, Turtle

# 定数定義
SCREEN_SIZE = 600
BOUNDARY_LIMIT = 270  # 600 * 0.9 / 2 = 270 (-270 <= x, y <= 270)
MOVE_DISTANCE = 10
TURN_ANGLE = 10
BG_COLOR = "#D3D3D3"
BORDER_COLOR = "red"
PEN_COLOR = "black"


def setup_frame(drawer: Turtle) -> None:
    """描画可能エリアの外枠（赤）とヘッダータイトルを静的に描画する。"""
    drawer.hideturtle()
    drawer.speed("fastest")
    drawer.penup()

    # 外枠の描画（幅20pxの赤枠）
    drawer.teleport(-BOUNDARY_LIMIT, -BOUNDARY_LIMIT)
    drawer.color(BORDER_COLOR)
    drawer.pensize(20)
    drawer.pendown()

    for _ in range(4):
        drawer.forward(BOUNDARY_LIMIT * 2)
        drawer.left(90)

    drawer.penup()

    # タイトルの文字入れ（上部中央）
    drawer.teleport(0, BOUNDARY_LIMIT + 5)
    drawer.color("white")
    drawer.write("Etch-a-Sketch", align="center", font=("Arial", 16, "bold"))


class EtchASketch:
    def __init__(self, tim: Turtle):
        self.tim = tim
        self.init_turtle_state()

    def init_turtle_state(self) -> None:
        """描画タートルの初期状態を設定する。"""
        self.tim.speed("fastest")
        self.tim.pensize(1)
        self.tim.color(PEN_COLOR)
        self.tim.shape("turtle")
        self.tim.penup()
        self.tim.home()  # 座標(0, 0)、角度0度にリセット
        self.tim.setheading(90)  # 上向きを開始方向とする
        self.tim.pendown()

    def is_within_boundary(self, next_x: float, next_y: float) -> bool:
        """指定した座標が描画制限エリア内（-270〜270）に収まっているか判定。"""
        return (-BOUNDARY_LIMIT <= next_x <= BOUNDARY_LIMIT) and (
            -BOUNDARY_LIMIT <= next_y <= BOUNDARY_LIMIT
        )

    def move_forward(self) -> None:
        """前進（境界外への移動はクランプして停止）。"""
        self.tim.forward(MOVE_DISTANCE)
        if not self.is_within_boundary(self.tim.xcor(), self.tim.ycor()):
            # 境界を超えた場合は直前の位置へ戻す（クランプ処理）
            self.tim.backward(MOVE_DISTANCE)

    def move_backward(self) -> None:
        """後退（境界外への移動はクランプして停止）。"""
        self.tim.backward(MOVE_DISTANCE)
        if not self.is_within_boundary(self.tim.xcor(), self.tim.ycor()):
            self.tim.forward(MOVE_DISTANCE)

    def turn_left(self) -> None:
        """反時計回りに回転。"""
        self.tim.left(TURN_ANGLE)

    def turn_right(self) -> None:
        """時計回りに回転。"""
        self.tim.right(TURN_ANGLE)

    def reset_canvas(self) -> None:
        """描画した線を消去し、タートルを初期状態に完全復帰させる。"""
        self.tim.clear()
        self.init_turtle_state()


def main() -> None:
    # スクリーン初期設定
    screen = Screen()
    screen.setup(width=SCREEN_SIZE, height=SCREEN_SIZE)
    screen.bgcolor(BG_COLOR)
    screen.title("Etch-a-Sketch")

    # 1. 装飾描画用タートル（外枠を描いたら役割終了）
    frame_drawer = Turtle()
    setup_frame(frame_drawer)

    # 2. ユーザー操作用タートル
    user_turtle = Turtle()
    app = EtchASketch(user_turtle)

    # イベントリスナーの登録（関数オブジェクトをそのまま渡す）
    screen.listen()
    screen.onkey(app.move_forward, "Up")
    screen.onkey(app.move_forward, "w")
    screen.onkey(app.move_backward, "Down")
    screen.onkey(app.move_backward, "s")
    screen.onkey(app.turn_left, "Left")
    screen.onkey(app.turn_left, "a")
    screen.onkey(app.turn_right, "Right")
    screen.onkey(app.turn_right, "d")
    screen.onkey(app.reset_canvas, "c")

    # ウィンドウの「×」閉じ時の例外を安全に終了
    try:
        screen.mainloop()
    except turtle.Terminator:
        pass


if __name__ == "__main__":
    main()
