import json
import requests


def get_google_trends(words_count: int = 7, locale_geo: str = "TW"):
    """取得 Google Trends 熱門關鍵字。"""
    print("\U0001F4E1 正在抓取 Google Trends 熱門關鍵字...")
    trends = []
    url = "https://trends.google.com/_/TrendsUi/data/batchexecute"
    payload = f'f.req=[[["i0OFE","[null,null,\\"{locale_geo}\\",0,null,24]"]]]'
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ 抓取 Trends 發生錯誤: {e}")
        return []

    def extract_json_from_response(text: str):
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
                "search_count": search_count,
            })
        except Exception:
            continue

    trends.sort(key=lambda x: x["search_count"], reverse=True)
    return trends[:words_count]
