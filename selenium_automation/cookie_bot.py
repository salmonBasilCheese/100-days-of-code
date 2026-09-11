import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TARGET_URL = "https://ozh.github.io/cookieclicker/"
CHECK_INTERVAL_SECONDS = 5.0
TOTAL_RUN_SECONDS = 300.0  # 5分間

options = Options()
options.add_argument("--window-size=1600,1000")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

# ブラウザ内で高速クリックを回すJS（Game.ClickCookie() を直接呼ぶ）
CLICK_BURST_SCRIPT = """
var clicks = arguments[0];
if (typeof Game !== 'undefined' && Game.ClickCookie) {
    for (var i = 0; i < clicks; i++) {
        Game.ClickCookie();
    }
}
"""

# Storeから購入可能な最高額の設備/アップグレードを一括購入するJS
AUTO_BUY_SCRIPT = """
if (typeof Game !== 'undefined') {
    // 1. アップグレードの購入（可能な限りすべて購入）
    for (var i = Game.UpgradesInStore.length - 1; i >= 0; i--) {
        var upgrade = Game.UpgradesInStore[i];
        if (upgrade && upgrade.canBuy()) {
            upgrade.buy();
        }
    }
    // 2. 設備（Buildings）の購入：最も高価な設備を優先して購入可能な限り買う
    for (var j = Game.ObjectsById.length - 1; j >= 0; j--) {
        var obj = Game.ObjectsById[j];
        if (obj && obj.locked === 0 && Game.cookies >= obj.price) {
            obj.buy(1);
            break; // 最高額のものを買ったら一度抜けてクッキーを温存または再判定
        }
    }
}
"""

try:
    print(f"[*] Cookie Clicker にアクセス中: {TARGET_URL}")
    driver.get(TARGET_URL)

    # 1. 初回言語選択の処理
    try:
        lang_select_en = wait.until(
            EC.element_to_be_clickable((By.ID, "langSelect-EN"))
        )
        print("[*] 言語選択モーダルを検出しました。'English' を選択します。")
        lang_select_en.click()
        time.sleep(3)
    except Exception:
        print("[*] 言語選択画面はスキップされました。")

    # 2. ゲーム内部エンジン（Game.ready）の起動完了を待機
    print("[*] ゲームエンジンの初期化を待機中...")
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script(
            "return typeof Game !== 'undefined' && Game.ready === 1;"
        )
    )
    print("[Success] ゲームエンジンが初期化されました。高速稼働を開始します。")

    start_time = time.time()
    last_check_time = start_time

    # 3. メインループ
    while time.time() - start_time < TOTAL_RUN_SECONDS:
        # 1回の往復で200回クリックを発火
        driver.execute_script(CLICK_BURST_SCRIPT, 200)

        current_time = time.time()

        # 4. 5秒ごとの Store 最適購入
        if current_time - last_check_time >= CHECK_INTERVAL_SECONDS:
            driver.execute_script(AUTO_BUY_SCRIPT)

            # 残高(cookies)、総クリック数(cookieClicks)、毎秒生産量(cookiesPs)を分離取得
            status = driver.execute_script("""
                return {
                    balance: Math.floor(Game.cookies),
                    clicks: Game.cookieClicks,
                    cps: Math.floor(Game.cookiesPs),
                    earned: Math.floor(Game.cookiesEarned)
                };
            """)
            print(
                f"[5秒経過] 総クリック回数: {status['clicks']:,} 回 | "
                f"所持残高: {status['balance']:,} | "
                f"毎秒生産(CpS): {status['cps']:,}"
            )
            last_check_time = current_time

    # 5. リザルト集計
    final_cookies = driver.execute_script("return Game.cookiesEarned;")
    final_cps = driver.execute_script("return Game.cookiesPs;")
    print("\n[Complete] 5分間の自動操縦が完了しました。")
    print(f"[*] 総獲得クッキー数: {final_cookies:,.0f}")
    print(f"[*] 最終 1秒あたり生産数 (CpS): {final_cps:,.1f}")

finally:
    print("[*] セッションを終了します。")
    driver.quit()
