import os
from datetime import datetime
from dotenv import load_dotenv

from utils import get_unique_path

load_dotenv()

CANVA_TEMPLATE_URL = os.getenv(
    "CANVA_TEMPLATE_URL",
    "https://www.canva.com/design/DAGpqS08mgg/ETfC__j_GCjnc3h0sG2haw/edit",
)
COOKIE_FILE = os.getenv("COOKIE_FILE", "canva_cookies.txt")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")


def get_caption_file() -> str:
    """取得今日的貼文文字檔路徑，若資料夾不存在則會建立。"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base_path = os.path.join(OUTPUT_DIR, f"{datetime.today().strftime('%Y%m%d')}_post_caption.txt")
    return get_unique_path(base_path)
