import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TARGET_PRODUCT_URL = os.getenv("TARGET_PRODUCT_URL")
TARGET_PRICE = int(os.getenv("TARGET_PRICE", "0"))
TARGET_DISCOUNT_PERCENT = float(os.getenv("TARGET_DISCOUNT_PERCENT", "0.0"))

TIMEOUT_SECONDS = 15

# Amazon の Bot 遮断を回避するための完全なブラウザ偽装ヘッダー
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,ja-JP;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Device-Memory": "8",
    "Viewport-Width": "1920",
}


def normalize_amazon_url(url: str) -> str:
    """冗長なパラメータや商品名スラッグを除去し、https://www.amazon.co.jp/dp/{ASIN} 形式に正規化する。"""
    match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
    if not match:
        raise ValueError(
            f"有効な Amazon ASIN（10桁の英数字）を検出できませんでした: {url}"
        )
    asin = match.group(1)
    return f"https://www.amazon.co.jp/dp/{asin}"


def clean_price_to_int(price_text: str) -> int:
    """価格文字列から記号や空白を除去し、int に変換する。"""
    cleaned = re.sub(r"[^\d]", "", price_text)
    if not cleaned:
        raise ValueError(f"価格文字列の数値変換に失敗しました: '{price_text}'")
    return int(cleaned)


def fetch_amazon_product_page(url: str) -> BeautifulSoup:
    """Amazon 商品ページの HTML を取得し、BeautifulSoup オブジェクトを返す。"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Error] HTTP 通信に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    # CAPTCHA / Bot 検知ページの判定
    if (
        "Robot Check" in response.text
        or "To discuss automated access to Amazon data" in response.text
    ):
        print(
            "[Warning] Amazon による Bot 遮断（CAPTCHA）が検知されました。",
            file=sys.stderr,
        )
        sys.exit(2)

    return BeautifulSoup(response.text, "html.parser")


def extract_product_details(soup: BeautifulSoup) -> dict:
    """HTML から商品名、現在価格、参考価格（割引前価格）を抽出する。"""
    # 1. 商品名の抽出
    title_element = soup.select_one("#productTitle")
    if not title_element:
        print(
            "[Error] 商品名（#productTitle）が取得できませんでした。", file=sys.stderr
        )
        sys.exit(1)
    product_title = title_element.get_text().strip()

    # 2. 現在価格のフォールバック抽出
    current_price = None
    price_selectors = [
        ".priceToPay span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div span.a-offscreen",
        "#corePrice_desktop span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price .a-offscreen",
    ]

    for selector in price_selectors:
        element = soup.select_one(selector)
        if element and element.get_text().strip():
            try:
                current_price = clean_price_to_int(element.get_text().strip())
                break
            except ValueError:
                continue

    if current_price is None:
        print("[Error] 現在価格を特定できませんでした。", file=sys.stderr)
        sys.exit(1)

    # 3. 参考価格（定価・割引前価格）の抽出（存在する場合のみ）
    original_price = None
    original_price_selectors = [
        ".basisPrice span.a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-text-price span.a-offscreen",
        "span.a-price.a-text-price span.a-offscreen",
    ]
    for selector in original_price_selectors:
        element = soup.select_one(selector)
        if element and element.get_text().strip():
            try:
                original_price = clean_price_to_int(element.get_text().strip())
                break
            except ValueError:
                continue

    # 割引率の計算
    discount_percent = 0.0
    if original_price and original_price > current_price:
        discount_percent = round(
            ((original_price - current_price) / original_price) * 100, 1
        )

    return {
        "title": product_title,
        "current_price": current_price,
        "original_price": original_price,
        "discount_percent": discount_percent,
    }


def send_discord_notification(product_data: dict, url: str) -> None:
    """Discord Webhook へ Embed 形式で価格低下アラートを送信する。"""
    if not DISCORD_WEBHOOK_URL:
        print("[Error] DISCORD_WEBHOOK_URL が設定されていません。", file=sys.stderr)
        sys.exit(1)

    embed = {
        "title": "🚨 Amazon 価格低下アラート",
        "description": f"[{product_data['title'][:100]}...]({url})",
        "color": 0x00FF00,  # 緑色
        "fields": [
            {
                "name": "現在価格",
                "value": f"¥{product_data['current_price']:,}",
                "inline": True,
            },
            {"name": "目標価格", "value": f"¥{TARGET_PRICE:,}", "inline": True},
        ],
        "footer": {"text": "Amazon Price Tracker Batch"},
    }

    if product_data["original_price"]:
        embed["fields"].append(
            {
                "name": "参考価格",
                "value": f"¥{product_data['original_price']:,}",
                "inline": True,
            }
        )
        embed["fields"].append(
            {
                "name": "割引率",
                "value": f"{product_data['discount_percent']}%",
                "inline": True,
            }
        )

    payload = {"embeds": [embed]}

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, json=payload, timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        print("[Success] Discord へ通知を送信しました。")
    except requests.RequestException as e:
        print(f"[Error] Discord への通知送信に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    if not TARGET_PRODUCT_URL:
        print("[Error] TARGET_PRODUCT_URL が設定されていません。", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Amazon 商品ページを検証中: {TARGET_PRODUCT_URL}")
    soup = fetch_amazon_product_page(TARGET_PRODUCT_URL)
    details = extract_product_details(soup)

    print(f"[Info] 商品名: {details['title'][:40]}...")
    print(f"[Info] 現在価格: ¥{details['current_price']:,}")
    if details["original_price"]:
        print(
            f"[Info] 参考価格: ¥{details['original_price']:,} (割引: {details['discount_percent']}%)"
        )

    # 条件判定: 目標価格以下 OR 目標割引率以上
    price_condition_met = (
        details["current_price"] <= TARGET_PRICE if TARGET_PRICE > 0 else False
    )
    discount_condition_met = (
        details["discount_percent"] >= TARGET_DISCOUNT_PERCENT
        if TARGET_DISCOUNT_PERCENT > 0
        else False
    )

    if price_condition_met or discount_condition_met:
        print("[*] 条件に合致しました。通知処理へ移行します。")
        send_discord_notification(details, TARGET_PRODUCT_URL)
    else:
        print(
            f"[*] 条件未達（現在価格: ¥{details['current_price']:,} > 目標: ¥{TARGET_PRICE:,} / "
            f"割引率: {details['discount_percent']}% < 目標: {TARGET_DISCOUNT_PERCENT}%）。通知はスキップされました。"
        )


if __name__ == "__main__":
    main()
