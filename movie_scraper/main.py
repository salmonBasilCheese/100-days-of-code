import sys
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

URL = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"
OUTPUT_FILE = "movies.txt"
EXPECTED_COUNT = 100
TIMEOUT_SECONDS = 15


def fetch_movie_titles() -> list[str]:
    """Wayback Machine から映画ランキングの HTML を取得し、タイトル一覧を昇順で抽出する。"""
    try:
        response = requests.get(URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        response.encoding = "utf-8"
    except RequestException as e:
        print(f"[Error] HTTP 通信に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    # HTML のパース（lxml が未導入の環境でも動くようフォールバックを設定）
    try:
        soup = BeautifulSoup(response.text, "lxml")
    except Exception:
        soup = BeautifulSoup(response.text, "html.parser")

    # タイトル要素（<h3 class="title">）の抽出
    title_tags = soup.find_all("h3", class_="title")

    # クラス名が一致しない場合のフォールバック（h3 タグ走査）
    if not title_tags:
        title_tags = [
            tag
            for tag in soup.find_all("h3")
            if any(char.isdigit() for char in tag.get_text())
        ]

    # 文字列のクレンジング（前後の余分な空白・改行を除去）
    movie_titles = [
        tag.get_text().strip() for tag in title_tags if tag.get_text().strip()
    ]

    # 件数の検証 (アサーション)
    if len(movie_titles) != EXPECTED_COUNT:
        print(
            f"[Warning] 抽出件数 ({len(movie_titles)} 件) が期待値 ({EXPECTED_COUNT} 件) と一致しません。",
            file=sys.stderr,
        )

    # Web ページ上は 100 位から降順で並んでいるため、1 位からの昇順に反転
    return movie_titles[::-1]


def save_to_file(titles: list[str], filepath: str) -> None:
    """昇順の映画タイトルリストを UTF-8 でファイルへ出力する。"""
    try:
        with open(filepath, mode="w", encoding="utf-8") as f:
            for title in titles:
                f.write(f"{title}\n")
        print(f"[Success] {len(titles)} 件のタイトルを '{filepath}' に保存しました。")
    except OSError as e:
        print(f"[Error] ファイル書き込みに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    print(f"[*] スクレイピングを開始します: {URL}")
    movies = fetch_movie_titles()
    save_to_file(movies, OUTPUT_FILE)


if __name__ == "__main__":
    main()
