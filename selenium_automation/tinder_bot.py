import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)

TARGET_URL = "https://tinder.com/"
MAX_SWIPES = 50  # 1回の実行における最大スワイプ回数（安全上限）
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 850

options = Options()
options.add_argument(f"--window-size={VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}")
# 通知プロンプトおよびパスワードマネージャーの無効化
options.add_experimental_option(
    "prefs",
    {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    },
)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)


def dismiss_popups():
    """突発的に割り込む各種モーダル（通知・ホーム画面追加・マッチ等）を検知して閉じる"""
    # 閉じる対象となるボタンの探索候補
    popup_xpaths = [
        # 位置情報・通知許可モーダルの「後で」「許可しない」系
        "//button[contains(., 'Not interested') or contains(., '後で') or contains(., 'Cancel') or contains(., 'I decline')]",
        # ホーム画面追加等の案内
        "//button[contains(., 'Not now') or contains(., '今はしない')]",
        # マッチング成立画面の閉じるボタン
        "//button[contains(., 'Back to Tinder') or contains(., 'Keep Swiping') or @title='Back to Tinder']",
        # Cookie同意バナー
        "//div[contains(text(), 'I accept') or contains(text(), '同意')]//ancestor::button",
    ]

    for xpath in popup_xpaths:
        try:
            btn = driver.find_element(By.XPATH, xpath)
            if btn.is_displayed():
                btn.click()
                print(f"[*] ポップアップを自動処理しました: {xpath}")
                time.sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException):
            continue


def check_out_of_likes():
    """Like上限（課金モーダル等）が表示されているか判定"""
    out_of_likes_indicators = [
        "//span[contains(text(), 'Out of Likes') or contains(text(), 'いいね！の上限')]",
        "//button[contains(., 'Get Tinder Plus') or contains(., 'Tinder Goldを取得')]",
    ]
    for xpath in out_of_likes_indicators:
        try:
            elem = driver.find_element(By.XPATH, xpath)
            if elem.is_displayed():
                return True
        except NoSuchElementException:
            pass
    return False


try:
    print(f"[*] Tinder Web にアクセス中: {TARGET_URL}")
    driver.get(TARGET_URL)

    # 1. 手動ログイン待機フェーズ
    print("[*] 認証画面を検知中...")
    print(
        "[!] 2段階認証/SMS認証がある場合は、開いたブラウザでログインを完了させてください（最大60秒待機）"
    )

    # スワイプ画面（メインカードまたはLikeボタン）が出現するまで同期待ち
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(@class, 'button')]//span[text()='Like'] | //body[.//div[contains(@class, 'recCard')]]",
                )
            )
        )
        print("[Success] ログインおよびスワイプ画面のロードを確認しました。")
    except TimeoutException:
        print("[*] 待機時間が経過しました。メイン画面の要素探索を試行します。")

    time.sleep(3)
    dismiss_popups()

    # 2. 自動スワイプ実行ループ
    swipes_completed = 0
    likes_given = 0

    print(f"[*] 自動スワイプループを開始します（上限: {MAX_SWIPES} 回）")
    body = driver.find_element(By.TAG_NAME, "body")

    for i in range(1, MAX_SWIPES + 1):
        # 割り込みモーダルを定期確認・破棄
        dismiss_popups()

        # Like制限（上限モーダル）のチェック
        if check_out_of_likes():
            print(
                "\n[!] 1日のLike上限に到達しました（または有料プランプロンプトを検知）。安全のため停止します。"
            )
            break

        try:
            # 人間らしいランダム遅延（1.3秒〜2.7秒）
            delay = random.uniform(1.3, 2.7)
            time.sleep(delay)

            # キーボード操作で右スワイプ（Like）を発火
            body.send_keys(Keys.ARROW_RIGHT)
            swipes_completed += 1
            likes_given += 1
            print(
                f"[*] スワイプ実行 [{swipes_completed}/{MAX_SWIPES}] (待機: {delay:.2f}s)"
            )

        except NoSuchElementException:
            # カードが読み込み中の可能性
            time.sleep(2)
            continue
        except Exception as e:
            print(
                f"[!] スワイプ中に例外を検知: {type(e).__name__}。ポップアップ解消を試みます。"
            )
            dismiss_popups()
            time.sleep(2)

    # 3. 実行結果サマリー
    print("\n--- スワイプ実行概要 ---")
    print(f"総スワイプ試行数 ： {swipes_completed}")
    print(f"Like 送信数      ： {likes_given}")
    print("-------------------------")

    time.sleep(2)

finally:
    print("[*] セッションを終了し、ブラウザを閉じます。")
    driver.quit()
