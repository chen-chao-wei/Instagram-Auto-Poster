import os
import time
import logging
from datetime import datetime

from settings import EXPORT_DIR


def get_unique_path(path: str) -> str:
    """Return a file path that does not overwrite existing files."""
    base, ext = os.path.splitext(path)
    counter = 1
    unique_path = path
    while os.path.exists(unique_path):
        unique_path = f"{base}({counter}){ext}"
        counter += 1
    return unique_path

def capture_screenshot(driver, output_dir: str, prefix: str = "error") -> str:
    """截圖並返回檔案路徑。"""
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{prefix}_{int(time.time())}.png")
    try:
        driver.save_screenshot(file_path)
        logging.info("已儲存截圖至 %s", file_path)
    except Exception as e:
        logging.error("截圖失敗: %s", e)
    return file_path

def wait_for_download(download_dir: str, file_name: str, timeout: int = 120):
    """等待 Canva 下載完成，並將檔案重新命名。"""
    search_name = "search top7.png"
    search_path = os.path.join(download_dir, search_name)
    target_path = get_unique_path(os.path.join(download_dir, file_name))
    end_time = time.time() + timeout

    while time.time() < end_time:
        if os.path.exists(search_path) and not os.path.exists(search_path + ".crdownload"):
            time.sleep(0.5)
            os.rename(search_path, target_path)
            logging.info("下載完成，檔案儲存於: %s", target_path)
            return target_path
        time.sleep(1)
    raise Exception(f"下載超時，找不到 {search_name}！")


def get_caption_file() -> str:
    """取得今日的貼文文字檔路徑，若資料夾不存在則會建立。"""

    os.makedirs(EXPORT_DIR, exist_ok=True)
    base_path = os.path.join(
        EXPORT_DIR,
        f"{datetime.today().strftime('%Y%m%d')}_post_caption.txt",
    )
    return get_unique_path(base_path)
