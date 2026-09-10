import datetime
import sys
import time
import requests
from bs4 import BeautifulSoup
from ytmusicapi import YTMusic

BILLBOARD_BASE_URL = "https://www.billboard.com/charts/hot-100"
HOT_100_START_DATE = datetime.date(1958, 8, 4)
TIMEOUT_SECONDS = 15
SEARCH_INTERVAL_SECONDS = 0.5  # レートリミット回避のための待機時間
AUTH_FILE = "browser.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_validated_date() -> str:
    """ユーザーから YYYY-MM-DD 形式で日付入力を受け付け、妥当性を検証する。"""
    today = datetime.date.today()
    while True:
        user_input = input("対象の日付を入力してください (YYYY-MM-DD): ").strip()
        try:
            target_date = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
        except ValueError:
            print(
                "[Error] 日付の形式が正しくありません。YYYY-MM-DD 形式で入力してください。",
                file=sys.stderr,
            )
            continue

        if target_date < HOT_100_START_DATE:
            print(
                f"[Error] {HOT_100_START_DATE} (Hot 100 創設日) 以降の日付を指定してください。",
                file=sys.stderr,
            )
            continue

        if target_date > today:
            print("[Error] 未来の日付は指定できません。", file=sys.stderr)
            continue

        return target_date.strftime("%Y-%m-%d")


def fetch_billboard_hot_100(date_str: str) -> list[dict[str, str]]:
    """指定された日付の Billboard Hot 100 をスクレイピングし、100件の楽曲リストを返す。"""
    url = f"{BILLBOARD_BASE_URL}/{date_str}/"
    print(f"[*] Billboard データを取得中: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"[Error] Billboard へのリクエストに失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    song_rows = soup.select("ul.o-chart-results-list-row-container")

    if not song_rows:
        song_rows = soup.select("div.o-chart-results-list-row-container")

    tracks: list[dict[str, str]] = []

    if song_rows:
        for row in song_rows:
            title_tag = row.select_one("li h3#title-of-a-story, h3#title-of-a-story")
            if not title_tag:
                continue

            title = title_tag.get_text().strip()
            artist_tag = title_tag.find_next_sibling("span")
            artist = artist_tag.get_text().strip() if artist_tag else ""

            tracks.append({"title": title, "artist": artist})
    else:
        title_tags = soup.select("li h3#title-of-a-story")
        for tag in title_tags:
            title = tag.get_text().strip()
            artist_tag = tag.find_next_sibling("span")
            artist = artist_tag.get_text().strip() if artist_tag else ""
            tracks.append({"title": title, "artist": artist})

    return tracks


def search_and_collect_video_ids(
    ytmusic: YTMusic, tracks: list[dict[str, str]]
) -> list[str]:
    """YouTube Music 上で各楽曲を検索し、Video ID のリストを作成する。"""
    video_ids: list[str] = []
    total = len(tracks)

    print(f"\n[*] YouTube Music で楽曲の検索を開始します (全 {total} 件)...")

    for i, track in enumerate(tracks, start=1):
        query = f"{track['title']} {track['artist']}".strip()
        try:
            results = ytmusic.search(query=query, filter="songs", limit=1)
            if results and "videoId" in results[0]:
                video_id = results[0]["videoId"]
                video_ids.append(video_id)
                print(f"[{i:03d}/{total:03d}] 発見: {track['title']} (ID: {video_id})")
            else:
                # songs でヒットしない場合は filter を外して再検索
                fallback_results = ytmusic.search(query=query, limit=1)
                if fallback_results and "videoId" in fallback_results[0]:
                    video_id = fallback_results[0]["videoId"]
                    video_ids.append(video_id)
                    print(
                        f"[{i:03d}/{total:03d}] 代替発見: {track['title']} (ID: {video_id})"
                    )
                else:
                    print(
                        f"[{i:03d}/{total:03d}] スキップ (未検出): {query}",
                        file=sys.stderr,
                    )
        except Exception as e:
            print(f"[{i:03d}/{total:03d}] 検索エラー: {query} ({e})", file=sys.stderr)

        # YouTube Music へのレート制限対策
        time.sleep(SEARCH_INTERVAL_SECONDS)

    return video_ids


def create_hot100_playlist(
    ytmusic: YTMusic, date_str: str, video_ids: list[str]
) -> str:
    """プレイリストを作成し、取得した Video ID を一括登録する。"""
    playlist_name = f"{date_str} Hot 100"
    description = f"Billboard Hot 100 on {date_str}. Generated automatically by Python."

    print(f"\n[*] プレイリスト '{playlist_name}' を作成中...")
    playlist_id = ytmusic.create_playlist(
        title=playlist_name, description=description, video_ids=video_ids
    )
    return playlist_id


def main() -> None:
    # 1. 認証チェック
    try:
        ytmusic = YTMusic(AUTH_FILE)
    except Exception as e:
        print(
            f"[Error] YouTube Music 認証に失敗しました。'ytmusicapi oauth' を実行済みか確認してください: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. 日付入力と Billboard スクレイピング
    target_date = get_validated_date()
    tracks = fetch_billboard_hot_100(target_date)

    if not tracks:
        print("[Error] 楽曲リストを取得できませんでした。", file=sys.stderr)
        sys.exit(1)

    print(f"[Success] Billboard Hot 100 から {len(tracks)} 件の楽曲を抽出しました。")

    # 3. 楽曲検索と Video ID 収集
    video_ids = search_and_collect_video_ids(ytmusic, tracks)
    print(f"\n[Result] 解決成功: {len(video_ids)} / {len(tracks)} 曲")

    if not video_ids:
        print("[Error] 追加可能な楽曲が 1 件も見つかりませんでした。", file=sys.stderr)
        sys.exit(1)

    # 4. プレイリスト作成と追加
    playlist_id = create_hot100_playlist(ytmusic, target_date, video_ids)
    playlist_url = f"https://music.youtube.com/playlist?list={playlist_id}"
    print(f"\n[Completed] プレイリストの作成が完了しました。")
    print(f"URL: {playlist_url}")


if __name__ == "__main__":
    main()
