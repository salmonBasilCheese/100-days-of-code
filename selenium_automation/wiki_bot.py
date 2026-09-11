import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

try:
    driver.maximize_window()
    driver.get("https://en.wikipedia.org/wiki/Main_Page")

    article_count_elem = driver.find_element(By.CSS_SELECTOR, "#articlecount a")
    print(f"[Info] 記事数リンクのテキスト: {article_count_elem.text}")

    # 1. 検索バーへキーワードを入力
    search_input = driver.find_element(By.NAME, "search")
    print("[*] 'Python' のキーワードを入力中...")
    search_input.send_keys("Python")

    time.sleep(1)

    # 2. DOM変更による StaleElementReferenceException を防ぐため、要素を再取得して Enter を送信
    search_input = driver.find_element(By.NAME, "search")
    print("[*] Enter キーを送信して検索を実行します。")
    search_input.send_keys(Keys.ENTER)

    time.sleep(2)
    print(f"[Success] 遷移後ページタイトル: {driver.title}")

finally:
    driver.quit()
