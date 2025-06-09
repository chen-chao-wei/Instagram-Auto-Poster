import os
from dotenv import load_dotenv

load_dotenv()

CANVA_TEMPLATE_URL = os.getenv(
    "CANVA_TEMPLATE_URL",
    "https://www.canva.com/design/DAGpqS08mgg/ETfC__j_GCjnc3h0sG2haw/edit",
)
COOKIE_FILE = os.getenv("COOKIE_FILE", "canva_cookies.txt")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
