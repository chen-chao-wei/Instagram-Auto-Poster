import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

from utils import wait_for_download, capture_screenshot
from settings import OUTPUT_DIR


def setup_canva_browser(template_url: str, cookie_file: str, output_dir: str):
    """啟動瀏覽器並載入 Canva Cookie。"""
    logging.info("啟動瀏覽器並載入 Canva 模板")
    options = uc.ChromeOptions()

    # 基本設定
    options.add_argument("--disable-notifications")

    # 下載相關設定
    chrome_prefs = {
        "download.default_directory": os.path.abspath(output_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safeBrowse.enabled": True,
    }
    options.add_experimental_option("prefs", chrome_prefs)

    driver = None
    try:
        driver = uc.Chrome(options=options)

        driver.get("https://www.canva.com")
        # Wait for the body element to be present before adding cookies
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            with open(cookie_file, "r") as f:
                raw_cookie = f.read().strip()
                for item in raw_cookie.split(";"):
                    if "=" in item:
                        name, value = item.strip().split("=", 1)
                        cookie_dict = {
                            "name": name,
                            "value": value,
                            "domain": ".canva.com",
                            "path": "/",
                        }
                        driver.add_cookie(cookie_dict)
        except FileNotFoundError:
            logging.error("找不到 Cookie 檔案: %s", cookie_file)
            if driver:
                capture_screenshot(driver, OUTPUT_DIR, "cookie_error")
            raise
        except Exception as e:
            logging.error("載入 Cookie 發生錯誤: %s", e)
            if driver:
                capture_screenshot(driver, OUTPUT_DIR, "cookie_error")
            raise
    except Exception as e:
        logging.error("啟動瀏覽器失敗: %s", e)
        if driver:
            capture_screenshot(driver, OUTPUT_DIR, "launch_error")
        raise

    driver.get(template_url)
    
    # Wait for the Canva editor's text fields to be present, which indicates the page is ready.
    # This is more reliable than a fixed sleep.
    # WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located((By.XPATH, '//div[@lang="zh-TW" and contains(@class, "AdBbhQ")]//span[@class="OYPEnA"]'))
    # )
    WebDriverWait(driver, 30).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )
    
    return driver

def clear_and_input(driver, target_span_element, text_to_input):
    """穩定地清空並輸入文字到指定元素。"""
    actions = ActionChains(driver)
    max_retry = 3
    for attempt in range(1, max_retry + 1):
        WebDriverWait(driver, 5).until(EC.visibility_of(target_span_element))
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(target_span_element))
        logging.info(f"雙擊span:{target_span_element.text}")
        actions.double_click(target_span_element).perform()
        time.sleep(0.2)

        try:
            editable_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            logging.info(f"找到可編輯區塊:{editable_div.text}")
            break
        except Exception:
            if attempt == max_retry:
                raise
    editable_div.send_keys(Keys.END)
    time.sleep(0.3)
    current_text = editable_div.text
    for _ in range(len(current_text)):
        editable_div.send_keys(Keys.BACK_SPACE)
        time.sleep(0.01)
    logging.info(f"輸入:{text_to_input}")
    editable_div.send_keys(text_to_input)
    time.sleep(0.3)
    actions.send_keys(Keys.ESCAPE).perform()
    actions.send_keys(Keys.ESCAPE).perform()

def fill_template(driver, top_keywords, today_str: str, mode: str = "fill", cta_str: str = "你今天查了哪一個? 分享給你的朋友吧!"):
    """在 Canva 模板中填入關鍵字資料或還原為預設文字。"""
    expected_labels = [
        "EnterTitle", "EnterKey1", "EnterTag1", "EnterKey2", "EnterTag2",
        "EnterKey3", "EnterTag3", "EnterKey4", "EnterTag4", "EnterKey5",
        "EnterTag5", "EnterKey6", "EnterTag6", "EnterKey7", "EnterTag7", "EnterCTA"
    ]

    # 預先處理 display_relate 字串長度
    processed_keywords = []
    for kw in top_keywords:
        display_relate = kw["relate"]
        if len(display_relate) >= 20:
            display_relate = display_relate[:20] + "..."
        processed_keywords.append({
            "topic": kw["topic"],
            "search_count": kw["search_count"],
            "relate": display_relate
        })

    if (mode == "fill"):
        keyword_spans = []
        for label in expected_labels:
            try:
                span = driver.find_element(By.XPATH, f'//div[@lang="zh-TW"]//span[text()="{label}"]')
                keyword_spans.append(span)
            except Exception:
                logging.error(f"找不到模板標籤文字: {label}")
                capture_screenshot(driver, OUTPUT_DIR, f"missing_{label}")
                raise
        
    if (mode == "reset"):
        try:
            # 取得 title 與 CTA span
            title_span = driver.find_element(By.XPATH, f'//div[@lang="zh-TW"]//span[contains(text(), "今日熱搜 Top 7（日期:{today_str}）")]')
            cta_span = driver.find_element(By.XPATH, f'//div[@lang="zh-TW"]//span[text()="{cta_str}"]')

            # 合併順序 title -> key -> CTA
            keyword_spans = [title_span]
            for label in processed_keywords:
                topic_span = driver.find_element(By.XPATH, f'//div[@lang="zh-TW"]//span[text()="{label["topic"]} {label["search_count"]:,}+"]')
                relate_span = driver.find_element(By.XPATH, f'//div[@lang="zh-TW"]//span[text()="#{label["relate"]}"]')
                keyword_spans.append(topic_span)
                keyword_spans.append(relate_span)
            keyword_spans.append(cta_span)
        except Exception:
            logging.error(f"找不到模板標籤文字: {label}")
            capture_screenshot(driver, OUTPUT_DIR, f"missing_{label}")
            raise

    if len(keyword_spans) != len(expected_labels):
        logging.error("可用欄位 %s 不等於預期數量 %s 個", len(keyword_spans), len(expected_labels))
        capture_screenshot(driver, OUTPUT_DIR, "fill_error")
        raise

    if mode == "reset":
        for span, label in zip(keyword_spans, expected_labels):
            clear_and_input(driver, span, label)
        return

    # mode == "fill"
    for idx, span in enumerate(keyword_spans):
        if idx == 0:
            clear_and_input(driver, span, f"今日熱搜 Top 7（日期:{today_str}）")
        elif 1 <= idx <= 14:
            kw_idx = (idx - 1) // 2
            if kw_idx >= len(processed_keywords):
                continue
            keyword = processed_keywords[kw_idx]
            if idx % 2 == 1:
                clear_and_input(driver, span, f"{keyword['topic']} {keyword['search_count']:,}+")
            else:
                clear_and_input(driver, span, f"#{keyword['relate']}")
        elif idx == 15:
            clear_and_input(driver, span, cta_str)

def download_image(driver, output_dir: str, file_name: str) -> str:
    """在 Canva 中下載圖片，並回傳檔案路徑。"""
    try:
        # Wait for the 'Share' button to be clickable and then click it.
        share_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., '分享')]"))
        )
        share_button.click()

        # Wait for the 'Download' button in the dropdown menu to be clickable.
        download_menu_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='下载']"))
        )
        download_menu_button.click()

        time.sleep(3) # TODO 經測試必須等待才能成功點擊下載
        # Wait for the final 'Download' button in the dialog to be clickable.
        final_download_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and span[text()='下载']]"))
        )
        final_download_button.click()

        path = wait_for_download(output_dir, file_name)
        WebDriverWait(driver, 30).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        body = driver.find_element(By.TAG_NAME, 'body')
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(body, 0, 0).click().perform()
        time.sleep(0.3)
        # time.sleep(10)
        return path
    except Exception as e:
        logging.error("下載圖片失敗: %s", e)
        capture_screenshot(driver, output_dir, "download_error")
        raise
