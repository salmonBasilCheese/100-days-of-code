import math
import random
import time
import turtle
from turtle import Screen, Turtle

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_TURTLES = 8

# コース設計
BASE_RADIUS_X = 260
BASE_RADIUS_Y = 160
LANE_WIDTH = 14

BOTTOM_ANGLE = -math.pi / 2  # 画面下部（ゴールライン）


def calculate_ellipse_circumference(a: float, b: float) -> float:
    """ラマヌジャンの楕円周長近似式"""
    h = ((a - b) ** 2) / ((a + b) ** 2)
    return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))


def get_random_color() -> tuple[int, int, int]:
    return (random.randint(0, 220), random.randint(0, 220), random.randint(0, 220))


class OvalTrack:
    def __init__(self):
        self.drawer = Turtle()
        self.drawer.hideturtle()
        self.drawer.speed("fastest")

    def draw(self) -> None:
        self.drawer.color("#BDC3C7")
        self.drawer.pensize(2)

        # 8本のレーンを描画
        for i in range(NUM_TURTLES):
            rx = BASE_RADIUS_X + (i * LANE_WIDTH)
            ry = BASE_RADIUS_Y + (i * LANE_WIDTH)
            self.drawer.penup()

            for deg in range(0, 365, 5):
                rad = math.radians(deg)
                x = rx * math.cos(rad)
                y = ry * math.sin(rad)
                if deg == 0:
                    self.drawer.teleport(x, y)
                    self.drawer.pendown()
                else:
                    self.drawer.goto(x, y)
            self.drawer.penup()

        # ゴールライン（コース幅ぴったりに配置）
        inner_y = -BASE_RADIUS_Y
        outer_y = -(BASE_RADIUS_Y + ((NUM_TURTLES - 1) * LANE_WIDTH))
        self.drawer.teleport(0, inner_y)
        self.drawer.color("red")
        self.drawer.pensize(3)
        self.drawer.pendown()
        self.drawer.goto(0, outer_y)
        self.drawer.penup()


class UIOverlay:
    def __init__(self):
        self.writer = Turtle()
        self.writer.hideturtle()
        self.writer.speed("fastest")
        self.writer.penup()

    def show_ready_message(self) -> None:
        self.writer.clear()
        self.writer.teleport(0, 15)
        self.writer.write(
            "TURTLE OVAL RACE", align="center", font=("Arial", 18, "bold")
        )
        self.writer.teleport(0, -15)
        self.writer.write(
            "Press [SPACE] to Bet & Start", align="center", font=("Arial", 13, "bold")
        )

    def show_result_message(self, winner_id: int, user_won: bool) -> None:
        self.writer.clear()
        self.writer.teleport(0, 25)
        self.writer.write(
            f"Winner: Turtle #{winner_id}!", align="center", font=("Arial", 20, "bold")
        )
        self.writer.teleport(0, -5)
        result_text = "You Won!" if user_won else "You Lost..."
        self.writer.write(result_text, align="center", font=("Arial", 16, "bold"))
        self.writer.teleport(0, -35)
        self.writer.write(
            "Press [SPACE] to Race Again", align="center", font=("Arial", 12, "normal")
        )

    def clear(self) -> None:
        self.writer.clear()


class OvalRacer:
    def __init__(self, racer_id: int, lane_index: int, target_race_distance: float):
        self.id = racer_id
        self.lane = lane_index
        self.rx = BASE_RADIUS_X + (lane_index * LANE_WIDTH)
        self.ry = BASE_RADIUS_Y + (lane_index * LANE_WIDTH)
        self.circumference = calculate_ellipse_circumference(self.rx, self.ry)
        self.target_race_distance = target_race_distance

        self.turtle = Turtle(shape="turtle")
        self.turtle.shapesize(0.6, 0.6)
        self.turtle.speed("fastest")
        self.turtle.penup()

        self.reset_to_start()

    def reset_to_start(self) -> None:
        self.turtle.color(get_random_color())

        excess_distance = self.circumference - self.target_race_distance
        offset_angle = (excess_distance / self.circumference) * (2 * math.pi)

        self.start_angle = BOTTOM_ANGLE + offset_angle
        self.current_angle = self.start_angle
        self.distance_traveled = 0.0
        self.update_position()

    def update_position(self) -> None:
        x = self.rx * math.cos(self.current_angle)
        y = self.ry * math.sin(self.current_angle)
        self.turtle.teleport(x, y)

        heading_deg = math.degrees(
            math.atan2(
                self.ry * math.cos(self.current_angle),
                -self.rx * math.sin(self.current_angle),
            )
        )
        self.turtle.setheading(heading_deg)

    def step(self) -> None:
        # 1周約10秒で完走する移動幅（1.8〜2.7 px/frame）
        delta_distance = random.uniform(1.8, 2.7)
        self.distance_traveled += delta_distance

        sin_t = math.sin(self.current_angle)
        cos_t = math.cos(self.current_angle)
        local_radius = math.sqrt((self.rx * sin_t) ** 2 + (self.ry * cos_t) ** 2)

        delta_theta = delta_distance / max(local_radius, 1.0)
        self.current_angle += delta_theta
        self.update_position()

    def is_finished(self) -> bool:
        return self.distance_traveled >= self.target_race_distance


class OvalGameManager:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.state = "READY"
        self.winner = None
        self.user_bet: int | None = None

        self.track = OvalTrack()
        self.track.draw()

        self.ui = UIOverlay()
        self.ui.show_ready_message()

        base_race_distance = calculate_ellipse_circumference(
            BASE_RADIUS_X, BASE_RADIUS_Y
        )
        self.racers = [
            OvalRacer(
                racer_id=i + 1, lane_index=i, target_race_distance=base_race_distance
            )
            for i in range(NUM_TURTLES)
        ]

        self.screen.listen()
        self.screen.onkey(self.handle_space, "space")

    def ensure_focus(self) -> None:
        self.screen.listen()
        try:
            canvas = self.screen.getcanvas()
            canvas.focus_force()
        except Exception:
            pass

    def prompt_user_bet(self) -> None:
        while True:
            raw_input = self.screen.textinput(
                title="Make your bet",
                prompt="Which turtle will win? Enter number (1-8):",
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

    def handle_space(self) -> None:
        if self.state == "READY":
            self.prompt_user_bet()
            self.start_race()
        elif self.state == "FINISHED":
            self.reset_game()

    def start_race(self) -> None:
        self.state = "RACING"
        self.ui.clear()
        self.winner = None

        try:
            while self.state == "RACING":
                for racer in self.racers:
                    racer.step()
                    if racer.is_finished():
                        self.winner = racer.id
                        self.state = "FINISHED"
                        break

                self.screen.update()
                time.sleep(0.016)

            if self.state == "FINISHED":
                user_won = self.user_bet == self.winner
                self.ui.show_result_message(self.winner, user_won)
                self.ensure_focus()
                self.screen.update()

        except turtle.Terminator:
            pass

    def reset_game(self) -> None:
        self.state = "READY"
        for racer in self.racers:
            racer.reset_to_start()
        self.ui.show_ready_message()
        self.screen.update()


def main() -> None:
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.bgcolor("white")
    screen.title("Oval Track Turtle Race")
    turtle.colormode(255)
    screen.tracer(0)

    OvalGameManager(screen)
    screen.update()

    try:
        screen.mainloop()
    except turtle.Terminator:
        pass


if __name__ == "__main__":
    main()
