import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoAlertPresentException,
)

TARGET_URL = "https://appbrewery.github.io/gym/"
EMAIL = "student@test.com"
PASSWORD = "password123"
TARGET_DAYS = ["tuesday", "tue", "thursday", "thu"]
MAX_RETRIES = 3
TIMEOUT_SECONDS = 15

options = Options()
options.add_argument("--window-size=1440,900")

# パスワードマネージャーおよび脆弱性アラートの無効化
options.add_experimental_option(
    "prefs",
    {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    },
)
options.add_argument("--disable-save-password-bubble")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, TIMEOUT_SECONDS)


def handle_browser_alert():
    try:
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(1)
    except NoAlertPresentException:
        pass


def safe_click(element):
    try:
        element.click()
    except (ElementClickInterceptedException, StaleElementReferenceException):
        driver.execute_script("arguments[0].click();", element)


def navigate_with_retry(url, max_attempts=MAX_RETRIES):
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[*] ページアクセス試行 ({attempt}/{max_attempts}): {url}")
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        except TimeoutException:
            print(f"[!] タイムアウト発生。リトライ中 ({attempt}/{max_attempts})...")
            time.sleep(2)
    raise TimeoutException(f"[Fatal] {url} へのアクセスに失敗しました。")


# --- 集計用カウンタ ---
count_booked = 0
count_waitlist = 0
count_already_booked = 0
count_tue_6pm = 0

try:
    # 1. サイトアクセス
    navigate_with_retry(TARGET_URL)

    # 2. ログイン画面への遷移
    print("[*] 'Login' ナビゲーションを探索中...")
    try:
        login_btn = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(text(), 'Login')] | //button[contains(text(), 'Login')]",
                )
            )
        )
        safe_click(login_btn)
        print("[*] 'Login' をクリックしました。")
    except TimeoutException:
        print("[*] 直接ログイン画面と判定します。")

    # 3. ログインフォーム入力
    print("[*] ログインフォームに入力中...")
    email_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='email' or @name='email' or @id='email']")
        )
    )
    password_input = driver.find_element(
        By.XPATH, "//input[@type='password' or @name='password' or @id='password']"
    )
    submit_btn = driver.find_element(
        By.XPATH, "//button[@type='submit'] | //input[@type='submit'] | //form//button"
    )

    email_input.clear()
    email_input.send_keys(EMAIL)
    password_input.clear()
    password_input.send_keys(PASSWORD)
    safe_click(submit_btn)

    print("[*] ログイン情報を送信しました。")
    time.sleep(1)
    handle_browser_alert()

    # 4. ログイン完了の同期
    print("[*] ログインセッション確立を待機中...")
    wait.until(
        EC.any_of(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//a[contains(text(), 'Bookings') or contains(text(), 'Logout')]",
                )
            ),
            EC.invisibility_of_element_located((By.XPATH, "//input[@type='password']")),
        )
    )
    print("[Success] ログイン成功。スケジュール画面を確認します。")
    time.sleep(2)

    # 5. スケジュールの解析と火曜・木曜枠の抽出
    booked_classes = []
    print("[*] スケジュールを走査中...")

    cards = driver.find_elements(
        By.XPATH,
        "//*[self::div or self::tr][.//button or .//a[contains(@class, 'btn')]]",
    )

    for card in cards:
        try:
            card_text = card.text.strip()
            if not card_text:
                continue

            card_text_lower = card_text.lower()

            # 対象曜日（火曜または木曜）が含まれているか判定
            if any(day in card_text_lower for day in TARGET_DAYS):
                summary = card_text.splitlines()[0]

                # 火曜日の午後6時（6:00 PM / 18:00）開始のクラス判定
                is_tue = "tue" in card_text_lower or "tuesday" in card_text_lower
                is_6pm = (
                    "6:00 pm" in card_text_lower
                    or "6pm" in card_text_lower
                    or "18:00" in card_text_lower
                )
                if is_tue and is_6pm:
                    count_tue_6pm += 1

                buttons = card.find_elements(
                    By.XPATH, ".//button | .//a[contains(@class, 'btn')]"
                )
                for btn in buttons:
                    b_text = btn.text.strip().lower()
                    if "book" in b_text and "booked" not in b_text:
                        print(f"[*] 予約を実行: {summary} -> '{btn.text}'")
                        safe_click(btn)
                        time.sleep(1)
                        booked_classes.append(summary)
                        count_booked += 1
                        break
                    elif "waitlist" in b_text:
                        print(f"[*] 待機リストに参加: {summary} -> '{btn.text}'")
                        safe_click(btn)
                        time.sleep(1)
                        booked_classes.append(f"{summary} (Waitlist)")
                        count_waitlist += 1
                        break
                    elif "booked" in b_text:
                        print(f"[*] 既に予約済み: {summary}")
                        count_already_booked += 1
                        break
        except StaleElementReferenceException:
            continue

    # 6. My Bookings で予約状態の検証
    print("\n[*] 'My Bookings' へ遷移して予約内容を確認します...")
    handle_browser_alert()

    try:
        my_bookings_link = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(text(), 'My Bookings') or contains(text(), 'Bookings')]",
                )
            )
        )
        safe_click(my_bookings_link)
    except TimeoutException:
        print("[!] My Bookings リンクが見つかりません。")

    time.sleep(2)
    page_content = driver.find_element(By.TAG_NAME, "body").text

    print("\n================ [ My Bookings 検証結果 ] ================")
    print(f"[*] 予約試行クラス一覧: {booked_classes}")
    for booked in booked_classes:
        clean_title = booked.replace(" (Waitlist)", "")
        if clean_title in page_content:
            print(f"[PASS] 予約/待機リスト反映確認: {booked}")
        else:
            print(f"[CHECK] 反映未確認（要手動確認）: {booked}")
    print("==========================================================")

    # 7. 指定フォーマットによる予約概要の表示
    print("\n--- 予約概要 ---")
    print(f"クラス数 予約済み ：   {count_booked}")
    print(f"待機リスト に参加した 人数：   {count_waitlist}")
    print(f"既に 予約済み ／ キャンセル待ち ：   {count_already_booked}")
    print(f"件数  火曜日の午後  6時開始 の授業処理 ：   {count_tue_6pm}件\n")

    time.sleep(2)

finally:
    print("[*] 全作業が終了しました。ブラウザウィンドウを閉じます。")
    driver.quit()
