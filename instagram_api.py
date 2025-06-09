import logging
import requests

from settings import IG_USER_ID, IG_ACCESS_TOKEN


class InstagramAPIError(Exception):
    pass


def create_media(image_url: str, caption: str) -> str:
    """Create media container and return its ID."""
    endpoint = f"https://graph.instagram.com/v21.0/{IG_USER_ID}/media"
    params = {
        "image_url": image_url,
        "caption": caption,
        "access_token": IG_ACCESS_TOKEN,
    }
    logging.info("\u767c\u8a00\u5230 Instagram ...")
    resp = requests.post(endpoint, params=params)
    try:
        resp.raise_for_status()
    except requests.RequestException as e:
        raise InstagramAPIError(f"Create media failed: {e}; {resp.text}")
    data = resp.json()
    return data.get("id")


def publish_media(creation_id: str) -> dict:
    """Publish the previously created media."""
    endpoint = f"https://graph.instagram.com/v21.0/{IG_USER_ID}/media_publish"
    params = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN,
    }
    resp = requests.post(endpoint, params=params)
    try:
        resp.raise_for_status()
    except requests.RequestException as e:
        raise InstagramAPIError(f"Publish media failed: {e}; {resp.text}")
    return resp.json()


def upload_and_publish(image_url: str, caption: str) -> dict:
    """Convenience function to create and publish a post."""
    creation_id = create_media(image_url, caption)
    if not creation_id:
        raise InstagramAPIError("Creation ID not returned")
    return publish_media(creation_id)
