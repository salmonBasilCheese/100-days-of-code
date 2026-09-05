import random
import time
import turtle
from turtle import Screen, Turtle

# 定数定義
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 400
NUM_TURTLES = 8
START_X = -210  # 番号表示スペースを確保するため少し右へ調整 (-230 -> -210)
GOAL_X = 230
MIN_STEP = 1
MAX_STEP = 10
Y_POSITIONS = [-140 + i * 40 for i in range(NUM_TURTLES)]  # [-140, -100, ..., 140]


def get_random_color() -> tuple[int, int, int]:
    """白背景との同化を防ぐため、RGB各値を 0〜235 の範囲で生成する。"""
    return (
        random.randint(0, 235),
        random.randint(0, 235),
        random.randint(0, 235),
    )


class RaceTrack:
    def __init__(self):
        self.drawer = Turtle()
        self.drawer.hideturtle()
        self.drawer.speed("fastest")
        self.drawer.penup()

    def draw_track_elements(self) -> None:
        """ゴールラインと各レーンのタートル番号を描画する。"""
        # 1. ゴールライン描画
        self.drawer.teleport(GOAL_X, -SCREEN_HEIGHT // 2 + 20)
        self.drawer.color("black")
        self.drawer.pensize(2)
        self.drawer.setheading(90)
        self.drawer.pendown()
        self.drawer.forward(SCREEN_HEIGHT - 40)
        self.drawer.penup()

        # 2. 各タートルの左側（スタート位置手前）に「#番号」を静的描画
        self.drawer.color("gray")
        for i, y_pos in enumerate(Y_POSITIONS):
            racer_id = i + 1
            # タートルの少し左・中央揃えで配置
            self.drawer.teleport(START_X - 25, y_pos - 7)
            self.drawer.write(
                f"#{racer_id}",
                align="center",
                font=("Arial", 11, "bold"),
            )


class ResultDisplay:
    def __init__(self):
        self.writer = Turtle()
        self.writer.hideturtle()
        self.writer.speed("fastest")
        self.writer.penup()

    def show_result(self, winners: list[int], user_won: bool) -> None:
        """勝者タートル番号とユーザー予想の勝敗を画面中央に表示する。"""
        self.writer.teleport(0, 20)
        if len(winners) == 1:
            winner_text = f"Winner: Turtle #{winners[0]}!"
        else:
            joined = ", ".join([f"#{w}" for w in winners])
            winner_text = f"Draw: Turtles {joined}!"

        user_text = "You Won!" if user_won else "You Lost..."

        self.writer.write(winner_text, align="center", font=("Arial", 16, "bold"))
        self.writer.teleport(0, -20)
        self.writer.write(user_text, align="center", font=("Arial", 16, "bold"))
        self.writer.teleport(0, -50)
        self.writer.write(
            "Press [SPACE] to Play Again",
            align="center",
            font=("Arial", 12, "normal"),
        )

    def clear(self) -> None:
        """表示文字を消去する。"""
        self.writer.clear()


class TurtleRacer:
    def __init__(self, racer_id: int, y_pos: int):
        self.id = racer_id
        self.initial_y = y_pos
        self.turtle = Turtle(shape="turtle")
        self.turtle.speed("fastest")
        self.turtle.penup()
        self.reset_to_start()

    def reset_to_start(self) -> None:
        """タートルを初期座標に戻し、新しいランダム色を適用する。"""
        self.turtle.color(get_random_color())
        self.turtle.teleport(START_X, self.initial_y)
        self.turtle.setheading(0)

    def step(self) -> None:
        """前進距離を1〜10pxの範囲でランダムに進める。"""
        distance = random.randint(MIN_STEP, MAX_STEP)
        self.turtle.forward(distance)

    def is_at_goal(self) -> bool:
        """中心X座標がゴールラインを超えているか判定。"""
        return self.turtle.xcor() >= GOAL_X


class GameManager:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.state = "READY"  # READY, RACING, FINISHED
        self.user_bet: int | None = None

        self.track = RaceTrack()
        self.track.draw_track_elements()
        self.result_display = ResultDisplay()

        self.racers = [
            TurtleRacer(racer_id=i + 1, y_pos=Y_POSITIONS[i])
            for i in range(NUM_TURTLES)
        ]

        self.screen.onkey(self.on_space_pressed, "space")

    def ensure_focus(self) -> None:
        """テキスト入力後に失われたキーボードフォーカスを強制的にキャンバスへ復帰させる。"""
        self.screen.listen()
        try:
            canvas = self.screen.getcanvas()
            canvas.focus_force()
        except Exception:
            pass

    def prompt_user_bet(self) -> None:
        """ユーザーから1〜8の番号を受け取る。"""
        while True:
            raw_input = self.screen.textinput(
                title="Make your bet",
                prompt="Which turtle will win the race? Enter number (1-8):",
            )
            if raw_input is None:
                self.user_bet = 1
                break

            cleaned = raw_input.strip()
            if cleaned.isdigit():
                val = int(cleaned)
                if 1 <= val <= NUM_TURTLES:
                    self.user_bet = val
                    break

        self.ensure_focus()

    def start_race(self) -> None:
        """レースを実行するメインループ。"""
        self.state = "RACING"
        winners = []

        try:
            while self.state == "RACING":
                for racer in self.racers:
                    racer.step()
                    if racer.is_at_goal():
                        winners.append(racer.id)

                if winners:
                    self.state = "FINISHED"
                    user_won = self.user_bet in winners
                    self.result_display.show_result(winners, user_won)
                    self.ensure_focus()
                    break

                self.screen.update()
                time.sleep(0.01)

        except turtle.Terminator:
            pass

    def on_space_pressed(self) -> None:
        """FINISHED 状態のときのみ再戦処理を行う。"""
        if self.state != "FINISHED":
            return

        self.state = "READY"
        self.result_display.clear()

        for racer in self.racers:
            racer.reset_to_start()
        self.screen.update()

        self.prompt_user_bet()
        self.start_race()


def main() -> None:
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.bgcolor("white")
    screen.title("Turtle Race")
    turtle.colormode(255)

    game = GameManager(screen)
    game.prompt_user_bet()
    game.start_race()

    try:
        screen.mainloop()
    except turtle.Terminator:
        pass


if __name__ == "__main__":
    main()
