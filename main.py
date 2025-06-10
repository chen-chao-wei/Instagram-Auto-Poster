from datetime import datetime
import os
import logging

from settings import (
    CANVA_TEMPLATE_URL,
    COOKIE_FILE,
    OUTPUT_DIR,
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    today = datetime.today()
    caption_file = get_caption_file()

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

    logging.info("\n已產出 IG 貼文文字：\n%s", '\n'.join(caption_lines))

    base_file = os.path.join(OUTPUT_DIR, f"{today.strftime('%Y%m%d')}_今日熱搜Top7.png")
    file_name = os.path.basename(get_unique_path(base_file))

    driver = None
    try:
        driver = setup_canva_browser(CANVA_TEMPLATE_URL, COOKIE_FILE, OUTPUT_DIR)
        fill_template(driver, top_keywords, today_display)
        image_path = download_image(driver, OUTPUT_DIR, file_name)
        logging.info("腳本已完成今日流程。")
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
            capture_screenshot(driver, OUTPUT_DIR, "critical_error")
    finally:
        if driver:
            input("\n⏳ 完成下載後，請按 Enter 關閉瀏覽器...")
            driver.quit()


if __name__ == '__main__':
    main()
