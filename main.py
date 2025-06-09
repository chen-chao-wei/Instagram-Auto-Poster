from datetime import datetime
import os

from config import CANVA_TEMPLATE_URL, COOKIE_FILE, OUTPUT_DIR, get_caption_file
from google_trends_api import get_google_trends
from canva_automation import launch_canva, fill_template, download_image


def main():
    today = datetime.today()
    caption_file = get_caption_file()

    top_keywords = get_google_trends(7)

    today_display = today.strftime('%-m/%-d')
    caption_lines = [f"\U0001F4CA 今日 Google 熱搜 Top 7（日期:{today_display}）\n"]
    for idx, item in enumerate(top_keywords, start=1):
        caption_lines.append(f"#{idx} {item['topic']}")
        caption_lines.append(f"🔍 關聯：{item['relate']}")
        caption_lines.append(f"🔥 {item['search_count']:,}+\n")
    caption_lines.append("你今天查了哪一個？ 分享給你朋友吧！")
    caption_lines.append("#google熱搜 #熱門關鍵字 #每日排行")

    with open(caption_file, 'w') as f:
        f.write('\n'.join(caption_lines))

    print("\n\U0001F4DD 已產出 IG 貼文文字：")
    print('\n'.join(caption_lines))

    file_name = f"{today.strftime('%Y%m%d')}_今日熱搜Top7.png"
    driver = launch_canva(CANVA_TEMPLATE_URL, COOKIE_FILE, OUTPUT_DIR)
    fill_template(driver, top_keywords, today_display)
    download_image(driver, OUTPUT_DIR, file_name)

    print("腳本已完成今日流程，請到 IG 發文，使用下載圖與文字檔案。")
    input("\n⏳ 完成下載後，請按 Enter 關閉瀏覽器...")
    # driver.quit()


if __name__ == '__main__':
    main()
