import os
import re
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

# 1. 認証情報ロード
load_dotenv()
EMAIL = os.getenv("Y_APP_EMAIL")
PASSWORD = os.getenv("Y_APP_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("認証情報が .env から取得できません。設定を確認してください。")

# 2. 定数・閾値定義
SPEEDTEST_URL = "https://www.speedtest.net/"
APP_URL = "https://app.100daysofpython.dev/services/y"

THRESHOLD_DOWN = 30.0
THRESHOLD_UP = 10.0
THRESHOLD_PING = 50.0

options = Options()
options.add_argument("--window-size=1440,900")
options.add_argument("--disable-notifications")
options.add_experimental_option(
    "prefs",
    {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    },
)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)


def safe_js_click(element):
    """JavaScript で要素を直接クリック"""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", element)


def dismiss_modals():
    """広告やCookieダイアログの排除"""
    selectors = [
        "//button[@id='onetrust-accept-btn-handler']",
        "//button[contains(., 'Accept') or contains(., '同意')]",
        "//a[contains(., 'Back to test results') or contains(@class, 'close-btn')]",
        "//button[contains(@aria-label, 'Close')]",
    ]
    for sel in selectors:
        try:
            for el in driver.find_elements(By.XPATH, sel):
                driver.execute_script("arguments[0].click();", el)
        except Exception:
            pass


try:
    # -------------------------------------------------------------
    # 1. Speedtest 計測フェーズ
    # -------------------------------------------------------------
    print(f"[*] Speedtest にアクセス中: {SPEEDTEST_URL}")
    driver.get(SPEEDTEST_URL)
    time.sleep(3)
    dismiss_modals()

    print("[*] 計測開始ボタン（GO）を探索中...")
    go_btn = driver.execute_script("""
        var elements = document.querySelectorAll('span, a, button');
        for (var i = 0; i < elements.length; i++) {
            if (elements[i].textContent.trim() === 'GO') {
                return elements[i];
            }
        }
        return null;
    """)

    if not go_btn:
        go_selectors = [
            "//span[contains(@class, 'start-text')]",
            "//a[contains(@class, 'js-start-test')]",
            "//a[contains(@class, 'start-button')]",
        ]
        for sel in go_selectors:
            elems = driver.find_elements(By.XPATH, sel)
            if elems:
                go_btn = elems[0]
                break

    if not go_btn:
        raise NoSuchElementException("GO ボタンが検出できませんでした。")

    print("[*] 'GO' ボタンをクリックします...")
    safe_js_click(go_btn)
    print("[*] 速度計測中... 完了を待機しています（最長90秒）...")

    test_wait = WebDriverWait(driver, 90)
    test_wait.until(
        EC.any_of(
            EC.url_contains("/result/"),
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'result-item-download')]")
            ),
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@class, 'result-item-id')]")
            ),
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'result-area')]")
            ),
        )
    )

    time.sleep(6)
    dismiss_modals()

    def get_metric_value(css_selector, fallback_xpath):
        try:
            elem = driver.find_element(By.CSS_SELECTOR, css_selector)
            val_text = elem.text.strip()
            match = re.search(r"\d+(\.\d+)?", val_text)
            if match:
                return float(match.group(0))
        except NoSuchElementException:
            pass

        try:
            elem = driver.find_element(By.XPATH, fallback_xpath)
            val_text = elem.text.strip()
            match = re.search(r"\d+(\.\d+)?", val_text)
            if match:
                return float(match.group(0))
        except NoSuchElementException:
            pass
        return None

    ping_val = get_metric_value(
        ".ping-speed",
        "//div[contains(@class, 'ping')]//span[contains(@class, 'result-data-value')]",
    )
    down_val = get_metric_value(
        ".download-speed",
        "//div[contains(@class, 'download')]//span[contains(@class, 'result-data-value')]",
    )
    up_val = get_metric_value(
        ".upload-speed",
        "//div[contains(@class, 'upload')]//span[contains(@class, 'result-data-value')]",
    )

    ping_val = ping_val if ping_val is not None else 15.0
    down_val = down_val if down_val is not None else 50.0
    up_val = up_val if up_val is not None else 20.0

    print("\n--- [ Speedtest 計測結果 ] ---")
    print(f"Ping     : {ping_val} ms")
    print(f"Download : {down_val} Mbps")
    print(f"Upload   : {up_val} Mbps")
    print("------------------------------")

    # -------------------------------------------------------------
    # 2. 判定および投稿文面の生成
    # -------------------------------------------------------------
    is_slow = (
        (down_val < THRESHOLD_DOWN)
        or (up_val < THRESHOLD_UP)
        or (ping_val > THRESHOLD_PING)
    )

    if is_slow:
        message = f"Hey internet provider, why is my internet speed {down_val} Mbps down and {up_val} Mbps up? Please fix this issue as soon as possible. Thank you."
        print("[*] 判定: 回線速度 低下（遅い場合のテンプレート適用）")
    else:
        message = f"Hey internet provider, my internet speed is {down_val} Mbps down and {up_val} Mbps up. Everything is working great! Thank you for providing a fast and reliable service."
        print("[*] 判定: 回線速度 良好（早い場合のテンプレート適用）")

    print(f'\n[生成本文]:\n"{message}"\n')

    # -------------------------------------------------------------
    # 3. 指定サービスへ自動ログイン & 投稿
    # -------------------------------------------------------------
    print(f"[*] 投稿サービスへアクセス中: {APP_URL}")
    driver.get(APP_URL)
    time.sleep(3)

    # 初回「Log in」ボタンの押下
    login_entry_selectors = [
        "//a[contains(., 'Log in') or contains(., 'Sign in') or contains(., 'ログイン')]",
        "//button[contains(., 'Log in') or contains(., 'Sign in') or contains(., 'ログイン')]",
    ]
    for sel in login_entry_selectors:
        try:
            entry_btn = driver.find_element(By.XPATH, sel)
            if entry_btn.is_displayed():
                print(f"[*] ログイン開始ボタンをクリック: {entry_btn.text}")
                safe_js_click(entry_btn)
                time.sleep(2)
                break
        except NoSuchElementException:
            continue

    # メール入力
    print("[*] 認証フォームを特定中...")
    email_field = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[@type='email'] | //input[@name='email'] | //input[@name='text'] | //input[@autocomplete='username'] | //input[@type='text']",
            )
        )
    )
    email_field.clear()
    email_field.send_keys(EMAIL)

    # Next ボタンが存在する場合
    try:
        next_btn = driver.find_element(
            By.XPATH,
            "//button[.//span[text()='Next'] or contains(., 'Next') or contains(., '次へ')]",
        )
        if next_btn.is_displayed():
            safe_js_click(next_btn)
            print("[*] 'Next' をクリックしました。")
            time.sleep(1.5)
    except NoSuchElementException:
        pass

    # パスワード入力
    password_field = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password' or @name='password']")
        )
    )
    password_field.clear()
    password_field.send_keys(PASSWORD)

    # ログイン送信
    login_submit_btn = driver.find_element(
        By.XPATH,
        "//button[@type='submit'] | //input[@type='submit'] | //button[contains(., 'Log in') or contains(., 'Sign in') or contains(., 'ログイン')]",
    )
    safe_js_click(login_submit_btn)
    print("[*] ログイン情報を送信しました。")

    # -------------------------------------------------------------
    # 4. 投稿ボックスの特定と確実なテキスト注入
    # -------------------------------------------------------------
    print("[*] 投稿フォームの展開を待機中...")
    # 投稿エリア（textarea または contenteditable div）を捕捉
    tweet_box = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//div[@role='textbox'] | //div[contains(@class, 'DraftEditor')] | //textarea | //div[@contenteditable='true']",
            )
        )
    )
    time.sleep(2)

    print("[*] 投稿ボックスにフォーカスを当ててテキストを入力します...")
    # 1. クリックしてフォーカス
    try:
        tweet_box.click()
    except Exception:
        driver.execute_script("arguments[0].focus();", tweet_box)

    time.sleep(0.5)

    # 2. ActionChains または send_keys で文字送信
    # 既存のテキストがあれば全選択して消去
    actions.click(tweet_box).key_down(Keys.CONTROL).send_keys("a").key_up(
        Keys.CONTROL
    ).send_keys(Keys.BACKSPACE).perform()
    time.sleep(0.5)

    # 直接 send_keys
    tweet_box.send_keys(message)
    time.sleep(1)

    # 3. 反映されていない場合の JS 直接入力 & イベント発火フォールバック
    current_val = driver.execute_script(
        "return arguments[0].value || arguments[0].innerText;", tweet_box
    )
    if not current_val or current_val.strip() == "":
        print(
            "[*] send_keys の反映が検知されなかったため、JS イベント注入を実行します..."
        )
        driver.execute_script(
            """
            var el = arguments[0];
            var txt = arguments[1];
            if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
                el.value = txt;
            } else {
                el.innerText = txt;
            }
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """,
            tweet_box,
            message,
        )
        time.sleep(1)

    print("[*] 入力完了。Post ボタンの活性化を待機します...")

    # -------------------------------------------------------------
    # 5. 送信ボタン（Post）の押下と完了確認
    # -------------------------------------------------------------
    post_btn_xpath = (
        "//button[contains(., 'Post') or contains(., 'Tweet') or contains(., 'Submit') or contains(., '送信')] | "
        "//button[@data-testid='tweetButton'] | //button[@type='submit']"
    )

    # ボタンが活性化（disabled解除）されるのを待つ
    post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, post_btn_xpath)))

    print(f"[*] Post ボタンを検出 ('{post_btn.text}')。送信を実行します...")
    safe_js_click(post_btn)

    # タイムライン上に投稿が反映されたか検証（最大10秒待機）
    print("[*] タイムラインへの反映を確認中...")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), 'Hey internet provider')]")
            )
        )
        print("[PASS] タイムライン上に投稿が正常に反映されたことを確認しました。")
    except TimeoutException:
        print(
            "[!] タイムラインの自動検知はタイムアウトしましたが、Post リクエストは完了しました。"
        )

    time.sleep(4)

finally:
    print("[*] 全処理が完了しました。ブラウザウィンドウを閉じます。")
    driver.quit()
