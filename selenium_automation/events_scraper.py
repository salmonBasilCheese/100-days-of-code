import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# バックグラウンド実行（ヘッドレス）はせず、動作確認のため通常起動
options = Options()
driver = webdriver.Chrome(options=options)

try:
    url = "https://www.python.org"
    driver.get(url)

    # 1. 指定されたセレクタで要素リストを取得
    time_elements = driver.find_elements(By.CSS_SELECTOR, ".event-widget time")
    title_elements = driver.find_elements(By.CSS_SELECTOR, ".event-widget li a")

    # 2. データの整合性検証（要素数が一致しているか）
    if len(time_elements) != len(title_elements):
        print(
            f"[Warning] 要素数が不一致です (time: {len(time_elements)}, title: {len(title_elements)})"
        )

    # 3. 辞書形式へのデータ構造化
    # {0: {'time': '...', 'name': '...'}, 1: ...}
    events_data = {
        index: {
            "time": time_elem.text,
            "name": title_elem.text,
        }
        for index, (time_elem, title_elem) in enumerate(
            zip(time_elements, title_elements)
        )
    }

    # 4. 結果の出力
    print("[Success] 抽出完了:")
    pprint.pprint(events_data)

finally:
    driver.quit()
