import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
)

# 1. URL 定義
ZILLOW_CLONE_URL = "https://appbrewery.github.io/Zillow-Clone/"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScWK5kFfjc0vQpvH8mij-WSFOO24BzEtmra5g4dyAOwWgrtJQ/viewform?usp=header"


# -----------------------------------------------------------------------------
# フェーズ 1: スクレイピング & データクレンジング (BeautifulSoup)
# -----------------------------------------------------------------------------
def scrape_zillow_data():
    print(f"[*] Zillow クローンからデータを取得中: {ZILLOW_CLONE_URL}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(ZILLOW_CLONE_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # 物件カード一覧のコンテナを取得
    cards = soup.select(".ListItem-c11n-8-84-3-StyledListCardWrapper")
    print(f"[*] 検出された物件カード数: {len(cards)}")

    links = []
    prices = []
    addresses = []

    for card in cards:
        # 1. リンクの抽出と完全URL化
        link_elem = card.select_one("a.property-card-link")
        if link_elem and link_elem.get("href"):
            href = link_elem["href"].strip()
            # 相対パスの場合はドメインを補完
            if not href.startswith("http"):
                href = f"https://www.zillow.com{href}"
            links.append(href)
        else:
            continue

        # 2. 価格の抽出と正規化 ($1,234 形式へ抽出)
        price_elem = card.select_one(".PropertyCardWrapper span") or card.select_one(
            "[data-test='property-card-price']"
        )
        if price_elem:
            raw_price = price_elem.text
            match = re.search(r"\$[\d,]+", raw_price)
            if match:
                prices.append(match.group(0))
            else:
                prices.append(raw_price.split("+")[0].split("/")[0].strip())
        else:
            prices.append("N/A")

        # 3. 住所の抽出と整形
        address_elem = card.select_one("address")
        if address_elem:
            raw_address = address_elem.text.strip()
            # パイプ記号や余分な改行のトリミング
            cleaned_address = raw_address.replace("\n", "").strip()
            if "|" in cleaned_address:
                cleaned_address = cleaned_address.split("|")[-1].strip()
            addresses.append(cleaned_address)
        else:
            addresses.append("N/A")

    # 整合性検証（アサーション）
    print(
        f"[*] 取得完了: リンク={len(links)}件, 価格={len(prices)}件, 住所={len(addresses)}件"
    )
    if not (len(links) == len(prices) == len(addresses)):
        raise ValueError(
            "抽出されたデータの件数に不整合が発生しています。セレクタを見直してください。"
        )

    return list(zip(addresses, prices, links))


# -----------------------------------------------------------------------------
# フェーズ 2: Google フォーム自動入力 (Selenium)
# -----------------------------------------------------------------------------
def enter_data_into_form(properties):
    print(
        f"\n[*] Google フォームへの自動入力を開始します（対象: {len(properties)} 件）..."
    )

    options = Options()
    options.add_argument("--window-size=1280,900")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    def safe_click(elem):
        try:
            elem.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", elem)

    try:
        for idx, (address, price, link) in enumerate(properties, start=1):
            driver.get(FORM_URL)
            print(f"[*] [{idx}/{len(properties)}] 送信中: {address} | {price}")

            # 3つのテキスト入力フィールドを特定
            # Googleフォームのテキストフィールドは通常 input[type='text']
            inputs = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//input[@type='text']"))
            )

            if len(inputs) < 3:
                raise ValueError(
                    f"入力フィールドが不足しています。検出数: {len(inputs)}"
                )

            # フォームの順序: 住所(Q1) -> 価格(Q2) -> リンク(Q3)
            # フィールドに値を入力
            inputs[0].clear()
            inputs[0].send_keys(address)

            inputs[1].clear()
            inputs[1].send_keys(price)

            inputs[2].clear()
            inputs[2].send_keys(link)

            # 送信ボタンを押下
            submit_btn = driver.find_element(
                By.XPATH,
                "//div[@role='button']//span[text()='送信' or text()='Submit'] | //button[contains(., '送信') or contains(., 'Submit')]",
            )
            safe_click(submit_btn)

            # 送信完了画面の待機
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//a[contains(text(), '別の回答を送信') or contains(text(), 'Submit another response')] | //*[contains(text(), '回答を記録しました') or contains(text(), 'Your response has been recorded')]",
                    )
                )
            )

            # 人間らしいディレイ
            time.sleep(1.0)

        print(
            f"\n[Success] 全 {len(properties)} 件の物件データをフォームへ正常に送信完了しました。"
        )

    finally:
        print("[*] ブラウザセッションを終了します。")
        driver.quit()


if __name__ == "__main__":
    extracted_properties = scrape_zillow_data()
    # サンプルプレビュー表示
    print("\n--- [ 抽出データプレビュー（先頭3件） ] ---")
    for item in extracted_properties[:3]:
        print(f"住所  : {item[0]}")
        print(f"価格  : {item[1]}")
        print(f"リンク: {item[2]}")
        print("-" * 40)

    # フォームへの自動入力実行
    enter_data_into_form(extracted_properties)
