import json
import time
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import os
import sys

# === 基本設定 ===
CANVA_TEMPLATE_URL = "https://www.canva.com/design/DAGpqS08mgg/ETfC__j_GCjnc3h0sG2haw/edit"
COOKIE_FILE = "canva_cookies.txt"  # 新格式的純文字 cookie
OUTPUT_DIR = "output"
CAPTION_FILE = os.path.join(OUTPUT_DIR, f"{datetime.today().strftime('%Y%m%d')}_post_caption.txt")

# === 建立資料夾 ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === 從 Google Trends 抓取熱門關鍵字（新 API） ===
def get_google_trends(words_count=7, locale_geo="TW"):
    print("\U0001F4E1 正在抓取 Google Trends 熱門關鍵字...")
    trends = []
    url = "https://trends.google.com/_/TrendsUi/data/batchexecute"
    payload = f'f.req=[[[\"i0OFE\",\"[null,null,\\\"{locale_geo}\\\",0,null,24]\"]]]'
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ 抓取 Trends 發生錯誤: {e}")
        return []

    def extract_json_from_response(text):
        for line in text.splitlines():
            trimmed = line.strip()
            if trimmed.startswith('[') and trimmed.endswith(']'):
                try:
                    intermediate = json.loads(trimmed)
                    data = json.loads(intermediate[0][2])
                    return data[1]
                except Exception:
                    continue
        return None

    trends_data = extract_json_from_response(response.text)
    if not trends_data:
        print("❌ 無法解析 Trends 資料")
        return []

    for item in trends_data:
        try:
            topic = item[0]
            search_count = item[6]
            related_terms = item[9][1:]
            trends.append({
                "topic": topic,
                "relate": "、".join(related_terms),
                "search_count": search_count
            })
        except Exception:
            continue
    
    # 根據 search_count 降序排序
    trends.sort(key=lambda x: x['search_count'], reverse=True)

    return trends[:words_count]


# === 輔助函式：判斷編輯屬性 ===
def is_editable(element):
    return element.get_attribute("contenteditable") == "true"

# === 輔助函式：穩定輸入內容 ===
def clear_and_input(target_span_element, text_to_input):
    """
    一個更穩定的函式，負責處理從點擊到輸入的完整流程。
    :param target_span_element: 要雙擊以啟動編輯的 span 元素。
    :param text_to_input: 要輸入的文字。
    """
    actions = ActionChains(driver)

    # 雙擊目標 span，使其進入編輯模式
    max_retry = 3
    for attempt in range(1, max_retry + 1):
        WebDriverWait(driver, 5).until(EC.visibility_of(target_span_element))
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(target_span_element))
        actions.double_click(target_span_element).perform()
        time.sleep(0.5)  # 給予反應時間
        try:
            editable_div = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            break  # 成功就跳出重試
        except Exception:
            print(f"⚠️ 第 {attempt} 次嘗試找不到可編輯輸入框")
            if attempt == max_retry:
                raise Exception(f"❌ {max_retry} 次雙擊都沒成功進入編輯模式。目標文字: {text_to_input}")
            time.sleep(0.3)  # 下次重試前稍等

    editable_div.send_keys(Keys.END)
    time.sleep(0.5)
    current_text = editable_div.text
    for _ in range(len(current_text)):
        editable_div.send_keys(Keys.BACK_SPACE)
        time.sleep(0.01)
    editable_div.send_keys(text_to_input)


# === 取得 Google 熱門關鍵字 Top 7 ===
top_keywords = get_google_trends(7)

# === 產出 IG 貼文文字 ===
today_str = datetime.today().strftime('%-m/%-d')
caption_lines = [f"\U0001F4CA 今日 Google 熱搜 Top 7（日期:{today_str}）\n"]
for idx, item in enumerate(top_keywords, start=1):
    caption_lines.append(f"#{idx} {item['topic']}")
    caption_lines.append(f"🔍 關聯：{item['relate']}")
    caption_lines.append(f"🔥 {item['search_count']:,}+\n")

cta_str = "你今天查了哪一個？ 分享給你朋友吧！"
caption_lines.append(cta_str)
caption_lines.append("#google熱搜 #熱門關鍵字 #每日排行")

with open(CAPTION_FILE, "w") as f:
    f.write("\n".join(caption_lines))

print("\n\U0001F4DD 已產出 IG 貼文文字：")
print("\n".join(caption_lines))

# === 啟動瀏覽器 + 載入 Cookie 並前往模板頁 ===
output_dir = "/Users/alfie/Documents/github/auto-ig-post/output"
today_str = datetime.today().strftime("%Y%m%d")
file_name = f"{today_str}_今日熱搜Top7.png"
file_path = os.path.join(output_dir, file_name)
print("\n\U0001F4BB 啟動 Chrome 並開啟 Canva 模板...")
options = uc.ChromeOptions()
options.add_argument("--disable-notifications")
chrome_prefs = {
    "download.default_directory": output_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", chrome_prefs)
driver = uc.Chrome(options=options)

driver.get("https://www.canva.com")
time.sleep(5)

with open(COOKIE_FILE, 'r') as f:
    raw_cookie = f.read().strip()
    for item in raw_cookie.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookie_dict = {
                'name': name,
                'value': value,
                'domain': '.canva.com',
                'path': '/',
            }
            driver.add_cookie(cookie_dict)

# 使用 cookie 後直接開啟模板頁
driver.get(CANVA_TEMPLATE_URL)
time.sleep(5)

# === 自動貼上文字 ===
print("\U0001F58A 自動貼上關鍵字...")

try:
    keyword_spans = driver.find_elements(By.XPATH, '//div[@lang="zh-TW" and contains(@class, "AdBbhQ")]//span[@class="OYPEnA"]')
    keyword_spans = sorted(keyword_spans, key=lambda el: el.location['y'])
    
    if len(keyword_spans) < 16: # 1標題 + 7*2關鍵字+關聯 + 1 CTA = 16
        print(f"⚠️ 可用欄位 {len(keyword_spans)} 不足，至少需 16 個")

    # 第 1 個：標題
    title_span = keyword_spans[0]
    # 直接呼叫新函式，傳入目標 span
    clear_and_input(title_span, f"今日熱搜 Top 7（日期:{today_str}）")
    time.sleep(1) # 完成一項操作後稍微等待

    # 從第 2 個開始：關鍵字段落
    for idx, keyword in enumerate(top_keywords):
        keyword_span_idx = 1 + idx * 2
        tag_span_idx = keyword_span_idx + 1

        print(f"執行關鍵字輸入: {keyword['topic']}")
        keyword_span = keyword_spans[keyword_span_idx]
        clear_and_input(keyword_span, f"{keyword['topic']} {keyword['search_count']:,}+")
        time.sleep(1)

        print(f"執行關聯詞輸入: {keyword['relate']}")
        tag_span = keyword_spans[tag_span_idx]
        # 判斷並截斷關聯詞
        display_relate = keyword['relate']
        if len(display_relate) >= 20:
            display_relate = display_relate[:20] + "..."

        clear_and_input(tag_span, f"#{display_relate}")
        time.sleep(1)

    print("✅ 標題與關鍵字內容已成功貼上")

except Exception as e:
    print("❌ 自動貼文失敗: ", e)
    import traceback
    traceback.print_exc()

def canva_auto_download_png(driver, output_dir, file_name, timeout=120):
    # 點擊「分享」按鈕
    WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., '分享')]"))
    ).click()
    time.sleep(1)

    # 點擊「下載」按鈕
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='下载']"))
    ).click()
    time.sleep(2)

    # 按下「下載」開始下載
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='下载']]"))
    ).click()

    # 等待下載完成（判斷 output_dir 有無 .crdownload）
    wait_for_download(output_dir, file_name, timeout=timeout)

def wait_for_download(download_dir, file_name, timeout=120):
    search_name = "search top7.png"
    search_path = os.path.join(download_dir, search_name)
    target_path = os.path.join(download_dir, file_name)
    end_time = time.time() + timeout

    while time.time() < end_time:
        # Canva 下載完會有這個檔名
        if os.path.exists(search_path) and not os.path.exists(search_path + ".crdownload"):
            # 保險多等 0.5 秒
            time.sleep(0.5)
            os.rename(search_path, target_path)
            print(f"✅ 下載完成，檔案儲存於: {target_path}")
            return
        time.sleep(1)
    raise Exception(f"下載超時，找不到 {search_name}！")

canva_auto_download_png(driver, output_dir, file_name)

print("腳本已完成今日流程，請到 IG 發文，使用下載圖與文字檔案。")

# === 保持開啟，待用戶下載完畢 ===
input("\n⏳ 完成下載後，請按 Enter 關閉瀏覽器...")
# driver.quit()
