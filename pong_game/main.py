import time
import turtle
from ball import Ball
from paddle import Paddle
from scoreboard import Scoreboard

WIN_SCORE = 5


def main() -> None:
    # 1. 画面初期化
    screen = turtle.Screen()
    screen.setup(width=800, height=600)
    screen.bgcolor("black")
    screen.title("Pong - AI Senior Engineer Clean Architecture")
    screen.tracer(0)

    # 2. インスタンス生成
    r_paddle = Paddle((350, 0))
    l_paddle = Paddle((-350, 0))
    ball = Ball()
    scoreboard = Scoreboard()

    # 3. 入力状態管理 (同時押し対応)
    keys_pressed: set[str] = set()

    def press_key(key: str) -> None:
        keys_pressed.add(key)

    def release_key(key: str) -> None:
        keys_pressed.discard(key)

    screen.listen()
    # Left Paddle: W / S
    screen.onkeypress(lambda: press_key("w"), "w")
    screen.onkeyrelease(lambda: release_key("w"), "w")
    screen.onkeypress(lambda: press_key("s"), "s")
    screen.onkeyrelease(lambda: release_key("s"), "s")

    # Right Paddle: Up / Down
    screen.onkeypress(lambda: press_key("Up"), "Up")
    screen.onkeyrelease(lambda: release_key("Up"), "Up")
    screen.onkeypress(lambda: press_key("Down"), "Down")
    screen.onkeyrelease(lambda: release_key("Down"), "Down")

    # 4. メインループ (例外安全)
    game_is_on = True
    try:
        while game_is_on:
            screen.update()
            time.sleep(ball.move_interval)

            # パドル移動 (押下中キーの処理)
            if "w" in keys_pressed:
                l_paddle.up()
            if "s" in keys_pressed:
                l_paddle.down()
            if "Up" in keys_pressed:
                r_paddle.up()
            if "Down" in keys_pressed:
                r_paddle.down()

            # ボール移動
            ball.move()

            # 上下壁の衝突判定 (ボール半径10px考慮)
            if ball.ycor() >= 290 and ball.dy > 0:
                ball.bounce_y()
            elif ball.ycor() <= -290 and ball.dy < 0:
                ball.bounce_y()

            # 右パドル衝突判定 (AABB矩形近似: xが330〜360 かつ パドル中心から±50px)
            if 330 <= ball.xcor() <= 360 and abs(ball.ycor() - r_paddle.ycor()) <= 50:
                ball.bounce_x_right_paddle()

            # 左パドル衝突判定 (AABB矩形近似: xが-360〜-330 かつ パドル中心から±50px)
            if -360 <= ball.xcor() <= -330 and abs(ball.ycor() - l_paddle.ycor()) <= 50:
                ball.bounce_x_left_paddle()

            # 得点判定: Player 1 (Left) 得点 -> Player 2 の失点 (サーブは右方向)
            if ball.xcor() > 390:
                scoreboard.l_point()
                if scoreboard.l_score >= WIN_SCORE:
                    scoreboard.show_game_over("PLAYER 1")
                    screen.update()
                    game_is_on = False
                else:
                    ball.reset_position(serve_direction=1)

            # 得点判定: Player 2 (Right) 得点 -> Player 1 の失点 (サーブは左方向)
            if ball.xcor() < -390:
                scoreboard.r_point()
                if scoreboard.r_score >= WIN_SCORE:
                    scoreboard.show_game_over("PLAYER 2")
                    screen.update()
                    game_is_on = False
                else:
                    ball.reset_position(serve_direction=-1)

        screen.exitonclick()

    except (turtle.Terminator, Exception):
        # ウィンドウの「×」閉じ等による異常終了時の安全な離脱
        pass


if __name__ == "__main__":
    main()
