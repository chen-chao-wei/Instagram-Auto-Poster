import base64
import logging
import os
import requests

from settings import GH_TOKEN, GH_REPO, GH_BRANCH


class GitHubAPIError(Exception):
    pass


def upload_image(file_path: str) -> str:
    """Upload image to a GitHub repository and return the raw URL."""
    if not GH_TOKEN or not GH_REPO:
        raise GitHubAPIError("GitHub configuration not set")
    file_name = os.path.basename(file_path)
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{file_name}"
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    data = {
        "message": "Upload image",
        "content": content,
        "branch": GH_BRANCH,
    }
    resp = requests.put(url, headers=headers, json=data)
    try:
        resp.raise_for_status()
    except requests.RequestException as e:
        raise GitHubAPIError(f"Upload failed: {e}; {resp.text}")
    data = resp.json()
    download_url = data.get("content", {}).get("download_url")
    if not download_url:
        download_url = (
            f"https://raw.githubusercontent.com/{GH_REPO}/{GH_BRANCH}/{file_name}"
        )
    logging.info("GitHub \u4e0a\u50b3\u6210\u529f: %s", download_url)
    return download_url
