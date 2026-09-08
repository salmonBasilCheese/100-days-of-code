from turtle import Turtle

INITIAL_DX = 10.0
INITIAL_DY = 10.0
INITIAL_INTERVAL = 0.05
MIN_INTERVAL = 0.015
MAX_SPEED_STEP = 18.0
SPEED_MULTIPLIER = 1.05
INTERVAL_MULTIPLIER = 0.90


class Ball(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("white")
        self.penup()
        self.dx = INITIAL_DX
        self.dy = INITIAL_DY
        self.move_interval = INITIAL_INTERVAL

    def move(self) -> None:
        """現在の速度ベクトルに基づいて移動"""
        self.setx(self.xcor() + self.dx)
        self.sety(self.ycor() + self.dy)

    def bounce_y(self) -> None:
        """上下壁との衝突反転 (符号反転)"""
        self.dy = -self.dy

    def bounce_x_right_paddle(self) -> None:
        """
        右パドルとの反射処理:
        - 符号固定: パドル内スタックを防ぐため、強制的に負の方向 (左向き) に設定
        - 加速処理: トンネリング防止のため上限 18px / tick でクランプ
        """
        self.dx = -min(abs(self.dx) * SPEED_MULTIPLIER, MAX_SPEED_STEP)
        self.dy = min(abs(self.dy) * SPEED_MULTIPLIER, MAX_SPEED_STEP) * (
            1 if self.dy > 0 else -1
        )
        self.move_interval = max(self.move_interval * INTERVAL_MULTIPLIER, MIN_INTERVAL)

    def bounce_x_left_paddle(self) -> None:
        """
        左パドルとの反射処理:
        - 符号固定: 強制的に正の方向 (右向き) に設定
        - 加速処理: 上限ガード付きで加速
        """
        self.dx = min(abs(self.dx) * SPEED_MULTIPLIER, MAX_SPEED_STEP)
        self.dy = min(abs(self.dy) * SPEED_MULTIPLIER, MAX_SPEED_STEP) * (
            1 if self.dy > 0 else -1
        )
        self.move_interval = max(self.move_interval * INTERVAL_MULTIPLIER, MIN_INTERVAL)

    def reset_position(self, serve_direction: int) -> None:
        """
        得点後のリセット処理:
        :param serve_direction: 1 (右向き / Player 2へのサーブ), -1 (左向き / Player 1へのサーブ)
        """
        self.goto(0, 0)
        self.move_interval = INITIAL_INTERVAL
        self.dx = INITIAL_DX * (1 if serve_direction > 0 else -1)
        self.dy = -self.dy  # 縦方向は直前の進行方向を反転
