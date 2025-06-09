import logging
import requests

from settings import IMGUR_CLIENT_ID


class ImgurAPIError(Exception):
    pass


def upload_image(file_path: str) -> str:
    """Upload image to Imgur and return the accessible link."""
    if not IMGUR_CLIENT_ID:
        raise ImgurAPIError("IMGUR_CLIENT_ID is not set")
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    try:
        with open(file_path, "rb") as f:
            files = {"image": f}
            resp = requests.post("https://api.imgur.com/3/image", headers=headers, files=files)
            resp.raise_for_status()
    except Exception as e:
        raise ImgurAPIError(f"Upload failed: {e}")
    data = resp.json()
    if not data.get("success"):
        raise ImgurAPIError(f"Upload failed: {data}")
    link = data.get("data", {}).get("link")
    logging.info("Imgur \u4e0a\u50b3\u6210\u529f: %s", link)
    return link
