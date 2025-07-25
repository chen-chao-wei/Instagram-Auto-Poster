from datetime import datetime
import os
import logging
import sys
import multiprocessing

from settings import (
    CANVA_TEMPLATE_URL,
    COOKIE_FILE,
    EXPORT_DIR,
    IG_USER_ID,
    IG_ACCESS_TOKEN,
    GH_TOKEN,
)
from instagram_api import upload_and_publish
from github_api import upload_image
from google_trends_api import get_google_trends
from canva_automation import setup_canva_browser, fill_template, download_image
from utils import capture_screenshot, get_unique_path, get_caption_file

def main():
    today = datetime.today()

    # 確保logs資料夾存在
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    logging.basicConfig(
        filename = os.path.join(logs_dir, f"{today.strftime('%Y%m%d')}_app.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # 取貼文文字檔路徑
    caption_file = get_caption_file()
    # 取得 Google Trends 熱門關鍵字。
    top_keywords = get_google_trends(7)

    today_display = today.strftime('%-m/%-d')
    caption_lines = [f"\U0001F4CA 今日 Google 熱搜 Top 7（日期:{today_display}）\n"]
    for idx, item in enumerate(top_keywords, start=1):
        caption_lines.append(f"#{item['topic']}")
        caption_lines.append(f"🔍 關聯：{item['relate']}")
        caption_lines.append(f"🔥 {item['search_count']:,}+\n")
    caption_lines.append("你今天查了哪一個？ 分享給你朋友吧！")
    caption_lines.append("#google熱搜 #熱門關鍵字 #每日排行")

    with open(caption_file, 'w') as f:
        f.write('\n'.join(caption_lines))

    logging.info("已產出 IG 貼文文字")

    image_name = os.path.basename(get_unique_path(os.path.join(EXPORT_DIR, f"{today.strftime('%Y%m%d')}_TodayTrendsTop7.png")))
    

    driver = None
    try:
        driver = setup_canva_browser(CANVA_TEMPLATE_URL, COOKIE_FILE, EXPORT_DIR)
        fill_template(driver, top_keywords, today_display)
        logging.info("已使用關鍵字取代Canva模板預設字")
        image_path = download_image(driver, EXPORT_DIR, image_name)
        logging.info("PNG存擋完成")
        fill_template(driver, top_keywords, today_display, "reset")
        logging.info("已復原Canva模板預設字")

        if IG_USER_ID and IG_ACCESS_TOKEN and GH_TOKEN:
            try:
                image_url = upload_image(image_path)
                upload_and_publish(image_url, "\n".join(caption_lines))
                logging.info("已自動發佈至 Instagram")
            except Exception as e:
                logging.error("自動發佈失敗: %s", e)
        else:
            logging.info("未設定 IG 或 GitHub 相關環境變數，請手動發佈 IG 貼文。")
    except Exception as e:
        logging.critical(f"自動化過程發生錯誤: {e}", exc_info=True)
        if driver:
            capture_screenshot(driver, EXPORT_DIR, "critical_error")
    finally:
        if driver:
            logging.info("關閉browser")
            driver.close()
            driver.quit()
        logging.info("已完成今日自動發文腳本")
        sys.exit()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
