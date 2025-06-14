import os
from dotenv import load_dotenv

load_dotenv()

CANVA_TEMPLATE_URL = os.getenv(
    "CANVA_TEMPLATE_URL",
    "https://www.canva.com/design/DAGpqS08mgg/ETfC__j_GCjnc3h0sG2haw/edit",
)
COOKIE_FILE = os.getenv("COOKIE_FILE", "canva_cookies.txt")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")

# Instagram API 設定
IG_USER_ID = os.getenv("IG_USER_ID", "")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")

# GitHub 上傳設定
GH_TOKEN = os.getenv("GH_TOKEN", "")
GH_REPO = os.getenv("GH_REPO", "chen-chao-wei/Image")
GH_BRANCH = os.getenv("GH_BRANCH", "main")
