import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    ElementNotInteractableException,
)

# 1. 認証情報ロード
load_dotenv()
USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("認証情報が .env から取得できません。設定を確認してください。")

BASE_URL = "https://app.100daysofpython.dev/services/share-a-naan"
LOGIN_URL = f"{BASE_URL}/welcome"
TARGET_USERNAME = "rordongamsay"

MAX_FOLLOWS = 20


class InstaFollower:
    def __init__(self):
        options = Options()
        options.add_argument("--window-size=1280,900")
        options.add_argument("--disable-notifications")
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            },
        )

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def safe_click(self, element):
        """通常クリックを試み、操作不能や干渉例外が発生した場合はJSで強制実行"""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def dismiss_save_info_modal(self):
        """ログイン後の『Save your login info?』モーダル（Not now）を破棄"""
        print("[*] ログイン情報保存モーダル（Not now）の有無を確認中...")
        time.sleep(2)

        # JS走査でテキストに 'Not now' または 'Not Now' を含む要素を直接クリック
        clicked = self.driver.execute_script("""
            var elements = document.querySelectorAll('button, a, div[role="button"], span');
            for (var i = 0; i < elements.length; i++) {
                var text = elements[i].textContent.trim().toLowerCase();
                if (text === 'not now' || text.includes('not now')) {
                    elements[i].click();
                    return true;
                }
            }
            return false;
        """)

        if clicked:
            print("[*] JS経由で 'Not now' をクリックしてモーダルを破棄しました。")
            time.sleep(1.5)
        else:
            print("[*] 保存モーダルは検出されませんでした。")

    def login(self):
        """ログインページにアクセスし認証を確立"""
        print(f"[*] ログインページにアクセス中: {LOGIN_URL}")
        self.driver.get(LOGIN_URL)

        user_field = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='username' or @type='text' or @type='email']")
            )
        )
        pass_field = self.driver.find_element(
            By.XPATH, "//input[@name='password' or @type='password']"
        )
        submit_btn = self.driver.find_element(
            By.XPATH,
            "//button[@type='submit'] | //input[@type='submit'] | //form//button",
        )

        user_field.clear()
        user_field.send_keys(USERNAME)
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        self.safe_click(submit_btn)

        print("[*] ログイン情報を送信しました。セッション確立を待機中...")
        self.wait.until(
            EC.any_of(
                EC.url_changes(LOGIN_URL),
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//nav | //div[contains(@class, 'feed')] | //span[contains(text(), 'doughboy')]",
                    )
                ),
            )
        )
        print("[Success] ログインに成功しました。")
        self.dismiss_save_info_modal()

    def find_followers(self):
        """画面上の doughboy を特定してプロフィールへ遷移し、フォロワー一覧を展開"""
        print(f"[*] ターゲットユーザー '{TARGET_USERNAME}' のリンクを探索中...")
        time.sleep(2)

        # ターゲットアカウントの要素を特定（Suggested欄またはストーリー）
        target_link = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"//a[contains(@href, '{TARGET_USERNAME}')] | "
                    f"//*[text()='{TARGET_USERNAME}']/ancestor::a | "
                    f"//*[text()='{TARGET_USERNAME}']",
                )
            )
        )
        print(f"[*] '{TARGET_USERNAME}' を画面上で検出。プロフィールへ遷移します...")
        self.safe_click(target_link)
        time.sleep(3)

        # プロフィール画面で「followers」リンクをクリック
        print("[*] フォロワー一覧リンクを探索中...")
        followers_link = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//a[contains(@href, 'followers')] | "
                    "//*[contains(text(), 'followers') or contains(text(), 'follower')]/ancestor::a | "
                    "//*[contains(text(), 'followers') or contains(text(), 'follower')]/ancestor::button | "
                    "//*[contains(text(), 'followers') or contains(text(), 'follower')]/ancestor::li | "
                    "//*[contains(text(), 'followers') or contains(text(), 'follower')]",
                )
            )
        )
        self.safe_click(followers_link)
        print("[*] フォロワーモーダルを展開しました。")
        time.sleep(2)

        # モーダル内のスクロールコンテナを特定
        print("[*] モーダル内のスクロールコンテナを特定中...")
        modal_container = self.driver.execute_script("""
            var dialog = document.querySelector("div[role='dialog'], .modal, .popup");
            if (dialog) {
                var scrollable = dialog.querySelector("div[style*='overflow'], ul, div.list");
                return scrollable || dialog;
            }
            return document.querySelector("div[role='dialog']") || document.querySelector("ul");
        """)

        # ポップアップ内をスクロールして追加フォロワーをロード
        print("[*] ポップアップ内をスクロールして追加フォロワーを読み込みます...")
        for i in range(2):
            if modal_container:
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    modal_container,
                )
            else:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
            time.sleep(2)
            print(f"[*] スクロール完了 ({i + 1}/2)")

    def follow(self):
        """モーダル内のフォローボタンを順次クリックし、既存フォロー例外を処理"""
        print(f"[*] フォロー処理を開始します（最大上限: {MAX_FOLLOWS} 件）...")

        followed_count = 0
        skipped_count = 0

        buttons = self.driver.find_elements(
            By.XPATH,
            "//div[@role='dialog']//button | //div[contains(@class, 'modal')]//button | //li//button",
        )
        print(f"[*] 検出されたボタン総数: {len(buttons)}")

        # --- 検証ログ追加ブロック ---
        for idx, btn in enumerate(buttons, 1):
            try:
                raw_text = btn.text.strip()
                aria_label = btn.get_attribute("aria-label") or ""
                print(f"[ボタン {idx}] text: '{raw_text}', aria-label: '{aria_label}'")
            except Exception as e:
                print(f"[ボタン {idx}] 取得失敗: {e}")
        # -----------------------------

        for btn in buttons:
            if followed_count >= MAX_FOLLOWS:
                print("[*] 設定された最大フォロー数に到達しました。")
                break

            try:
                btn_text = btn.text.strip().lower()
            except StaleElementReferenceException:
                continue

            # フォローボタンのみを対象
            if (
                "follow" in btn_text
                and "following" not in btn_text
                and "unfollow" not in btn_text
            ):
                try:
                    time.sleep(1.0)
                    btn.click()
                    followed_count += 1
                    print(f"[*] フォロー成功 [{followed_count}/{MAX_FOLLOWS}]")

                except (
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                ):
                    print("[!] 例外発生: 既にフォロー済みまたは確認モーダルが出現。")
                    try:
                        cancel_btn = self.driver.find_element(
                            By.XPATH, "//button[text()='Cancel' or text()='キャンセル']"
                        )
                        self.safe_click(cancel_btn)
                        print(
                            "[*] 'Cancel' ボタンをクリックしてオーバーレイを閉じました。"
                        )
                        skipped_count += 1
                        time.sleep(1.0)
                    except NoSuchElementException:
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1.0)

                except StaleElementReferenceException:
                    continue

        print("\n--- 実行サマリー ---")
        print(f"新規フォロー完了数 : {followed_count}")
        print(f"例外回避・スキップ数 : {skipped_count}")
        print("---------------------\n")

    def close(self):
        """ブラウザセッションの終了"""
        print("[*] 全作業が完了しました。ブラウザを終了します。")
        self.driver.quit()


if __name__ == "__main__":
    bot = InstaFollower()
    try:
        bot.login()
        bot.find_followers()
        bot.follow()
    finally:
        bot.close()
