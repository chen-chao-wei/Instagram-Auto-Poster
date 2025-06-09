import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from utils import clear_and_input, wait_for_download, capture_screenshot
from config import OUTPUT_DIR


def launch_canva(template_url: str, cookie_file: str, output_dir: str):
    """啟動瀏覽器並載入 Canva Cookie。"""
    logging.info("啟動瀏覽器並載入 Canva 模板")
    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")
    chrome_prefs = {
        "download.default_directory": os.path.abspath(output_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", chrome_prefs)
    driver = None
    try:
        driver = uc.Chrome(options=options)

        driver.get("https://www.canva.com")
        time.sleep(5)

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
    time.sleep(5)
    return driver


def fill_template(driver, top_keywords, today_str: str):
    """在 Canva 模板中填入關鍵字資料。"""
    try:
        keyword_spans = driver.find_elements(By.XPATH, '//div[@lang="zh-TW" and contains(@class, "AdBbhQ")]//span[@class="OYPEnA"]')
    except Exception as e:
        logging.error("取得模板欄位失敗: %s", e)
        capture_screenshot(driver, OUTPUT_DIR, "fill_error")
        raise
    keyword_spans = sorted(keyword_spans, key=lambda el: el.location['y'])

    if len(keyword_spans) < 16:
        logging.warning("可用欄位 %s 不足，至少需 16 個", len(keyword_spans))

    title_span = keyword_spans[0]
    clear_and_input(driver, title_span, f"今日熱搜 Top 7（日期:{today_str}）")
    time.sleep(1)

    for idx, keyword in enumerate(top_keywords):
        keyword_span_idx = 1 + idx * 2
        tag_span_idx = keyword_span_idx + 1

        logging.info("執行關鍵字輸入: %s", keyword['topic'])
        keyword_span = keyword_spans[keyword_span_idx]
        clear_and_input(driver, keyword_span, f"{keyword['topic']} {keyword['search_count']:,}+")
        time.sleep(1)

        logging.info("執行關聯詞輸入: %s", keyword['relate'])
        tag_span = keyword_spans[tag_span_idx]
        display_relate = keyword['relate']
        if len(display_relate) >= 20:
            display_relate = display_relate[:20] + "..."
        clear_and_input(driver, tag_span, f"#{display_relate}")
        time.sleep(1)


def download_image(driver, output_dir: str, file_name: str):
    """在 Canva 中下載圖片。"""
    try:
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., '分享')]"))
        ).click()
        time.sleep(1)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='下载']"))
        ).click()
        time.sleep(2)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[span[text()='下载']]"))
        ).click()

        wait_for_download(output_dir, file_name)
    except Exception as e:
        logging.error("下載圖片失敗: %s", e)
        capture_screenshot(driver, output_dir, "download_error")
        raise
