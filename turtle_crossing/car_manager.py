import random
from turtle import Turtle

COLORS = [
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "yellow",
    "teal",
    "magenta",
    "coral",
    "crimson",
    "gold",
    "dodgerblue",
]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 2
MAX_CAR_SPEED = 16.0
SPAWN_X = 300
DESPAWN_X = -320
Y_BOTTOM_ROAD = -240
Y_TOP_ROAD = 240
# 生成確率: 1/7 に緩和（0.05秒間隔ループで約0.5秒に1台生成）
SPAWN_CHANCE_MAX = 7


class CarManager:
    def __init__(self):
        self.all_cars: list[Turtle] = []
        self.car_speed = STARTING_MOVE_DISTANCE

    def create_car(self) -> None:
        """確率的に新規車両を生成 (1/7)"""
        if random.randint(1, SPAWN_CHANCE_MAX) == 1:
            new_car = Turtle("square")
            new_car.shapesize(stretch_wid=1, stretch_len=2)  # 幅 40px × 高さ 20px
            new_car.penup()
            new_car.color(random.choice(COLORS))
            random_y = random.randint(Y_BOTTOM_ROAD, Y_TOP_ROAD)
            new_car.goto(SPAWN_X, random_y)
            self.all_cars.append(new_car)

    def move_cars(self) -> None:
        """全車両を前進させ、画面外のインスタンスを破棄"""
        active_cars: list[Turtle] = []
        for car in self.all_cars:
            car.backward(self.car_speed)
            if car.xcor() < DESPAWN_X:
                car.hideturtle()
            else:
                active_cars.append(car)
        self.all_cars = active_cars

    def speed_up(self) -> None:
        """難易度上昇時の加速処理 (最大 16px/tick にクランプ)"""
        self.car_speed = min(self.car_speed + MOVE_INCREMENT, MAX_CAR_SPEED)

    def reset(self) -> None:
        """リトライ時の初期化: 既存の車を全消去し速度をリセット"""
        for car in self.all_cars:
            car.hideturtle()
        self.all_cars.clear()
        self.car_speed = STARTING_MOVE_DISTANCE
