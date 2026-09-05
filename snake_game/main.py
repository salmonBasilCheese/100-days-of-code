import random
import time
import turtle
from turtle import Screen, Turtle

# 定数定義
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20
MOVE_DISTANCE = 20
WALL_LIMIT = 280
STARTING_POSITIONS = [(0, 0), (-20, 0), (-40, 0)]
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0


class Snake:
    def __init__(self):
        self.segments: list[Turtle] = []
        self.create_snake()
        self.head = self.segments[0]

    def create_snake(self) -> None:
        for position in STARTING_POSITIONS:
            self.add_segment(position)

    def add_segment(self, position: tuple[float, float]) -> None:
        segment = Turtle(shape="square")
        segment.color("white")
        segment.penup()
        segment.speed("fastest")
        segment.teleport(position[0], position[1])
        self.segments.append(segment)

    def extend(self) -> None:
        """最後尾セグメントの位置に新しいセグメントを追加して体を伸ばす。"""
        self.add_segment(self.segments[-1].position())

    def move(self) -> None:
        """追従アルゴリズム: 後ろのセグメントから順に前の位置へスライド移動。"""
        for seg_idx in range(len(self.segments) - 1, 0, -1):
            prev_x = self.segments[seg_idx - 1].xcor()
            prev_y = self.segments[seg_idx - 1].ycor()
            self.segments[seg_idx].teleport(prev_x, prev_y)
        self.head.forward(MOVE_DISTANCE)

    def set_heading(self, heading: int) -> None:
        """180度逆走を禁止するインターロック制御。"""
        current_heading = self.head.heading()
        if heading == UP and current_heading != DOWN:
            self.head.setheading(UP)
        elif heading == DOWN and current_heading != UP:
            self.head.setheading(DOWN)
        elif heading == LEFT and current_heading != RIGHT:
            self.head.setheading(LEFT)
        elif heading == RIGHT and current_heading != LEFT:
            self.head.setheading(RIGHT)


class Food:
    def __init__(self):
        self.food = Turtle(shape="circle")
        self.food.color("blue")
        self.food.penup()
        self.food.shapesize(0.5, 0.5)  # 直径10px
        self.food.speed("fastest")
        self.refresh([])

    def refresh(self, snake_segments: list[Turtle]) -> None:
        """ヘビの体と重ならない20の倍数のグリッド座標へランダム配置。"""
        while True:
            # -280 から 280 までの 20の倍数を生成
            rand_x = (
                random.randint(-WALL_LIMIT // GRID_SIZE, WALL_LIMIT // GRID_SIZE)
                * GRID_SIZE
            )
            rand_y = (
                random.randint(-WALL_LIMIT // GRID_SIZE, WALL_LIMIT // GRID_SIZE)
                * GRID_SIZE
            )

            # 体内リスポーンの防止チェック
            overlap = any(seg.distance(rand_x, rand_y) < 15 for seg in snake_segments)
            if not overlap:
                self.food.teleport(rand_x, rand_y)
                break

    def position(self) -> tuple[float, float]:
        return self.food.position()


class Scoreboard:
    def __init__(self):
        self.score = 0
        self.writer = Turtle()
        self.writer.hideturtle()
        self.writer.color("white")
        self.writer.penup()
        self.writer.speed("fastest")
        self.update_score()

    def update_score(self) -> None:
        self.writer.clear()
        self.writer.teleport(0, 260)
        self.writer.write(
            f"Score: {self.score}", align="center", font=("Arial", 14, "bold")
        )

    def increase_score(self) -> None:
        self.score += 1
        self.update_score()

    def game_over(self) -> None:
        self.writer.teleport(0, 0)
        self.writer.color("red")
        self.writer.write("GAME OVER", align="center", font=("Arial", 24, "bold"))


class InputManager:
    """キー押下状態（set）を追跡し、同時押し排他制御を行うクラス。"""

    def __init__(self, screen: Screen, snake: Snake):
        self.screen = screen
        self.snake = snake
        self.pressed_keys: set[str] = set()

        # 各キーの押下・解放リスナー設定
        for key in ["Up", "w", "Down", "s", "Left", "a", "Right", "d"]:
            self.screen.onkeypress(lambda k=key: self.key_down(k), key)
            self.screen.onkeyrelease(lambda k=key: self.key_up(k), key)

    def key_down(self, key: str) -> None:
        self.pressed_keys.add(key)

    def key_up(self, key: str) -> None:
        self.pressed_keys.discard(key)

    def process_input(self) -> None:
        """
        フレームごとに呼び出し。
        押下キーがちょうど1方向のときのみ方向転換を受け付ける（同時押し時は無効化）。
        """
        # 方向ごとにグループ化
        active_directions = set()
        if "Up" in self.pressed_keys or "w" in self.pressed_keys:
            active_directions.add(UP)
        if "Down" in self.pressed_keys or "s" in self.pressed_keys:
            active_directions.add(DOWN)
        if "Left" in self.pressed_keys or "a" in self.pressed_keys:
            active_directions.add(LEFT)
        if "Right" in self.pressed_keys or "d" in self.pressed_keys:
            active_directions.add(RIGHT)

        # ちょうど1方向のみ押されている場合のみ方向を変更
        if len(active_directions) == 1:
            target_heading = active_directions.pop()
            self.snake.set_heading(target_heading)


def main() -> None:
    # 画面の初期設定
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.bgcolor("black")
    screen.title("Snake Game")
    screen.tracer(0)

    # 各モジュールのインスタンス化
    snake = Snake()
    food = Food()
    scoreboard = Scoreboard()
    input_manager = InputManager(screen, snake)

    screen.listen()

    # 初期描画
    screen.update()

    game_is_on = True
    try:
        while game_is_on:
            screen.update()
            time.sleep(0.1)

            # 入力の処理（同時押しチェック）
            input_manager.process_input()

            # ヘビの前進
            snake.move()

            # 1. エサとの衝突判定（捕獲）
            if snake.head.distance(food.position()) < 15:
                food.refresh(snake.segments)
                snake.extend()
                scoreboard.increase_score()

            # 2. 壁との衝突判定（境界値: ±280）
            if (
                snake.head.xcor() > WALL_LIMIT
                or snake.head.xcor() < -WALL_LIMIT
                or snake.head.ycor() > WALL_LIMIT
                or snake.head.ycor() < -WALL_LIMIT
            ):
                game_is_on = False
                scoreboard.game_over()
                screen.update()

            # 3. 自己衝突判定（頭と首以降の全セグメントとの距離判定）
            for segment in snake.segments[1:]:
                if snake.head.distance(segment) < 10:
                    game_is_on = False
                    scoreboard.game_over()
                    screen.update()
                    break

        screen.mainloop()

    except turtle.Terminator:
        # ウィンドウの×ボタン押下時の安全終了
        pass


if __name__ == "__main__":
    main()
