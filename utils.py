import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_unique_path(path: str) -> str:
    """Return a file path that does not overwrite existing files."""
    base, ext = os.path.splitext(path)
    counter = 1
    unique_path = path
    while os.path.exists(unique_path):
        unique_path = f"{base}({counter}){ext}"
        counter += 1
    return unique_path


def is_editable(element) -> bool:
    """判斷元素是否可編輯。"""
    return element.get_attribute("contenteditable") == "true"


def clear_and_input(driver, target_span_element, text_to_input):
    """穩定地清空並輸入文字到指定元素。"""
    actions = ActionChains(driver)
    max_retry = 3
    for attempt in range(1, max_retry + 1):
        WebDriverWait(driver, 5).until(EC.visibility_of(target_span_element))
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(target_span_element))
        actions.double_click(target_span_element).perform()
        time.sleep(0.5)
        try:
            editable_div = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            break
        except Exception:
            if attempt == max_retry:
                raise
            time.sleep(0.3)

    editable_div.send_keys(Keys.END)
    time.sleep(0.5)
    current_text = editable_div.text
    for _ in range(len(current_text)):
        editable_div.send_keys(Keys.BACK_SPACE)
        time.sleep(0.01)
    editable_div.send_keys(text_to_input)


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
