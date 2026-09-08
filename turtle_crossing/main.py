import time
import turtle
from car_manager import CarManager
from player import Player
from scoreboard import Scoreboard

COLLISION_DIST_X = 25
COLLISION_DIST_Y = 20
LOOP_SLEEP_SEC = 0.05


def main() -> None:
    # 1. 画面初期化
    screen = turtle.Screen()
    screen.setup(width=600, height=600)
    screen.bgcolor("white")
    screen.title("Turtle Crossing - Day 23")
    screen.tracer(0)

    # 2. インスタンス生成
    player = Player()
    car_manager = CarManager()
    scoreboard = Scoreboard()

    # 3. 状態管理
    is_game_over = False

    def handle_up() -> None:
        """ゲームオーバー時は前進入力を無効化"""
        if not is_game_over:
            player.go_up()

    def restart_game() -> None:
        """Spaceキーによる再プレイ処理"""
        nonlocal is_game_over
        if is_game_over:
            car_manager.reset()
            player.go_to_start()
            scoreboard.reset()
            is_game_over = False

    # 4. 入力バインド
    screen.listen()
    screen.onkeypress(handle_up, "Up")
    screen.onkeypress(restart_game, "space")

    # 5. メインループ (例外安全)
    running = True
    try:
        while running:
            time.sleep(LOOP_SLEEP_SEC)
            screen.update()

            # プレイ中のみゲーム内時間を進行
            if not is_game_over:
                # 車の生成と移動
                car_manager.create_car()
                car_manager.move_cars()

                # 衝突判定
                for car in car_manager.all_cars:
                    if (
                        abs(player.xcor() - car.xcor()) < COLLISION_DIST_X
                        and abs(player.ycor() - car.ycor()) < COLLISION_DIST_Y
                    ):
                        is_game_over = True
                        scoreboard.game_over()
                        break

                # ゴール到達判定
                if player.is_at_finish_line():
                    player.go_to_start()
                    car_manager.speed_up()
                    scoreboard.increase_level()

        screen.exitonclick()

    except (turtle.Terminator, Exception):
        pass


if __name__ == "__main__":
    main()
