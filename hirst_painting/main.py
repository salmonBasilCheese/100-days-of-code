import os
import random
import turtle
from turtle import Screen, Turtle

# 定数定義
IMAGE_FILE = "image.jpg"
DOT_SIZE = 20
DOT_SPACING = 50
GRID_SIZE = 10  # 10x10
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# 画像取得失敗時や白抜き除外後に使用するフォールバックカラー
FALLBACK_COLORS = [
    (198, 12, 32),
    (248, 222, 126),
    (43, 101, 236),
    (34, 139, 34),
    (255, 140, 0),
    (128, 0, 128),
]


def extract_colors(file_path: str, color_count: int = 30) -> list[tuple[int, int, int]]:
    """画像から色を抽出し、背景と同化する白系統を除外したRGBタプルリストを返す。"""
    if not os.path.exists(file_path):
        print(f"Warning: '{file_path}' not found. Falling back to default palette.")
        return FALLBACK_COLORS

    try:
        import colorgram

        extracted = colorgram.extract(file_path, color_count)
        rgb_colors = []

        for color in extracted:
            r = color.rgb.r
            g = color.rgb.g
            b = color.rgb.b
            # 白・オフホワイト・極端に薄いグレーを除外（境界値フィルター）
            if r > 235 and g > 235 and b > 235:
                continue
            rgb_colors.append((r, g, b))

        if not rgb_colors:
            print("Warning: No valid colors after filtering. Using fallback palette.")
            return FALLBACK_COLORS

        return rgb_colors

    except Exception as e:
        print(f"Unexpected error extracting colors: {e}. Using fallback palette.")
        return FALLBACK_COLORS


def calculate_start_position(grid_size: int, spacing: int) -> tuple[float, float]:
    """グリッド全体が画面中央に配置されるよう、左下の開始座標 (x, y) を計算する。"""
    # グリッドの総描画幅 = (ドット数 - 1) * 間隔
    total_span = (grid_size - 1) * spacing
    start_x = -(total_span / 2)
    start_y = -(total_span / 2)
    return start_x, start_y


def draw_hirst_painting(tim: Turtle, colors: list[tuple[int, int, int]]) -> None:
    """10x10のグリッド状にランダムな色のドットを描画する。"""
    start_x, start_y = calculate_start_position(GRID_SIZE, DOT_SPACING)

    for row in range(GRID_SIZE):
        # 各行の左端へ移動（線を描かずにワープ）
        current_y = start_y + (row * DOT_SPACING)
        tim.teleport(start_x, current_y)

        for col in range(GRID_SIZE):
            current_x = start_x + (col * DOT_SPACING)
            tim.teleport(current_x, current_y)
            chosen_color = random.choice(colors)
            tim.dot(DOT_SIZE, chosen_color)


def main() -> None:
    # 画面設定
    screen = Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    turtle.colormode(255)

    # 描画パフォーマンスの最適化: アニメーションを停止し瞬時に描画完了させる
    screen.tracer(0)

    # タートルの初期設定
    tim = Turtle()
    tim.hideturtle()
    tim.penup()

    # カラーパレットの取得と描画
    palette = extract_colors(IMAGE_FILE)
    draw_hirst_painting(tim, palette)

    # 描画の最終反映と画面維持
    screen.update()
    screen.exitonclick()


if __name__ == "__main__":
    main()
