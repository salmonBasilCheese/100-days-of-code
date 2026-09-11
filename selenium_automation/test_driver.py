import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ブラウザ起動オプションの設定
options = Options()
# スクリプト終了時にブラウザを即座に閉じない設定（目視確認用）
options.add_experimental_option("detach", True)

print("[*] Chrome WebDriver を初期化中...")
driver = webdriver.Chrome(options=options)

try:
    print("[*] Python 公式サイトへアクセス中...")
    driver.get("https://www.python.org")

    # ページタイトルを取得して出力
    page_title = driver.title
    print(f"[Success] 取得したタイトル: {page_title}")

    time.sleep(3)

finally:
    print("[*] ブラウザセッションを終了します。")
    driver.quit()
