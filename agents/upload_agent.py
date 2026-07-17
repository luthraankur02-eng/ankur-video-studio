import os
import json
import requests
from config import YT_CLIENT_SECRET_PATH, INSTAGRAM_ACCESS_TOKEN, CHANNELS

# ─────────────────────────────────────────────
# YOUTUBE UPLOAD
# ─────────────────────────────────────────────

def upload_youtube(
    video_path: str,
    title: str,
    description: str,
    hashtags: list,
    channel_key: str,
    credentials_json: str = None  # OAuth token JSON string ya path
) -> dict:
    """
    YouTube pe video upload karo.
    credentials_json: OAuth2 credentials (access_token, refresh_token etc.)
    Returns: { "video_id": str, "url": str }
    """
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    # Credentials load karo
    if credentials_json:
        if os.path.exists(credentials_json):
            with open(credentials_json) as f:
                creds_data = json.load(f)
        else:
            creds_data = json.loads(credentials_json)

        creds = Credentials(
            token         = creds_data.get("token"),
            refresh_token = creds_data.get("refresh_token"),
            token_uri     = creds_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id     = creds_data.get("client_id"),
            client_secret = creds_data.get("client_secret"),
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        raise Exception("YouTube credentials nahi diye. OAuth token chahiye.")

    youtube  = build("youtube", "v3", credentials=creds)
    channel  = CHANNELS[channel_key]

    # Tags banao
    tags = [h.lstrip("#") for h in hashtags] + [channel["name"]]

    # Shorts ke liye #Shorts hashtag zaroori
    if channel["duration_s"] <= 60:
        if "#Shorts" not in hashtags:
            tags.append("Shorts")
        full_description = f"{description}\n\n#Shorts"
    else:
        full_description = description

    body = {
        "snippet": {
            "title":       title[:100],
            "description": full_description[:5000],
            "tags":        tags[:30],
            "categoryId":  "22",  # People & Blogs
        },
        "status": {
            "privacyStatus":           "public",
            "selfDeclaredMadeForKids": channel_key == "doodle_masti",
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype     = "video/mp4",
        resumable    = True,
        chunksize    = 1024 * 1024  # 1MB chunks
    )

    request  = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None

    # Resumable upload
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"YouTube upload: {int(status.progress() * 100)}%")

    video_id = response["id"]
    return {
        "video_id": video_id,
        "url":      f"https://www.youtube.com/watch?v={video_id}",
        "platform": "youtube"
    }


# ─────────────────────────────────────────────
# INSTAGRAM REELS UPLOAD
# ─────────────────────────────────────────────

def upload_instagram(
    video_path: str,
    caption: str,
    hashtags: list,
    ig_user_id: str = None,
    access_token: str = None
) -> dict:
    """
    Instagram Reels upload karo (Graph API).
    Requirements:
    - Professional/Creator account
    - Facebook Page connected
    - video_path must be publicly accessible URL (direct file nahi chalega)
    
    IMPORTANT: Instagram Graph API local file upload nahi karta.
    Video pehle kisi public URL pe host karna padega (Firebase Storage, S3, etc.)
    Returns: { "media_id": str, "status": str }
    """
    token   = access_token or INSTAGRAM_ACCESS_TOKEN
    user_id = ig_user_id or os.getenv("INSTAGRAM_USER_ID", "")

    if not token or not user_id:
        raise Exception("Instagram credentials missing: INSTAGRAM_ACCESS_TOKEN aur INSTAGRAM_USER_ID chahiye")

    # NOTE: video_path yahan ek PUBLIC URL hona chahiye
    if not video_path.startswith("http"):
        raise Exception(
            "Instagram upload ke liye video pehle public URL pe host karo. "
            "Local path kaam nahi karega. Firebase Storage ya Railway static hosting use karo."
        )

    full_hashtags = " ".join(hashtags)
    full_caption  = f"{caption}\n\n{full_hashtags}"

    # Step 1: Media container banao
    container_url = f"https://graph.facebook.com/v19.0/{user_id}/media"
    container_data = {
        "media_type":  "REELS",
        "video_url":   video_path,
        "caption":     full_caption[:2200],
        "access_token": token
    }

    resp = requests.post(container_url, data=container_data, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Instagram container create failed: {resp.text}")

    container_id = resp.json().get("id")
    if not container_id:
        raise Exception(f"Container ID nahi mila: {resp.json()}")

    # Step 2: Container publish karo
    publish_url = f"https://graph.facebook.com/v19.0/{user_id}/media_publish"
    publish_data = {
        "creation_id":  container_id,
        "access_token": token
    }

    pub_resp = requests.post(publish_url, data=publish_data, timeout=30)
    if pub_resp.status_code != 200:
        raise Exception(f"Instagram publish failed: {pub_resp.text}")

    media_id = pub_resp.json().get("id")
    return {
        "media_id": media_id,
        "status":   "published",
        "platform": "instagram"
    }
