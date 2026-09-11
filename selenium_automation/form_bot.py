import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

try:
    driver.maximize_window()
    driver.get("https://appbrewery.github.io/fake-newsletter-signup/")

    # 1. 各入力フィールドの特定とデータ投入
    first_name_input = driver.find_element(By.NAME, "fName")
    last_name_input = driver.find_element(By.NAME, "lName")
    email_input = driver.find_element(By.NAME, "email")

    first_name_input.send_keys("Nishiki")
    last_name_input.send_keys("Hosokawa")
    email_input.send_keys("dummy@gmail.com")

    # 2. 送信ボタンの特定とクリック
    submit_button = driver.find_element(By.CSS_SELECTOR, "form button")
    submit_button.click()

    time.sleep(3)
    print("[Success] フォームの入力および送信が完了しました。")

finally:
    driver.quit()
