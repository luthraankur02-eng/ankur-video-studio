import os
import uuid
import requests
from config import PEXELS_API_KEY, TEMP_FOOTAGE_DIR

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"

def fetch_footage(keywords: list, duration_needed_s: int, orientation: str = "portrait", job_id: str = None) -> dict:
    """
    Pexels se stock footage download karo
    orientation: "portrait" (Shorts/Reels) ya "landscape" (YouTube)
    Returns: { "clips": [{"path": str, "duration": int}], "total_duration": int }
    """
    os.makedirs(TEMP_FOOTAGE_DIR, exist_ok=True)

    file_id    = job_id or str(uuid.uuid4())[:8]
    clips      = []
    total_dur  = 0
    clip_index = 0

    headers = {"Authorization": PEXELS_API_KEY}

    for keyword in keywords:
        if total_dur >= duration_needed_s:
            break

        params = {
            "query":       keyword,
            "orientation": orientation,  # portrait / landscape / square
            "size":        "medium",
            "per_page":    5,
            "min_duration": 3,
            "max_duration": 15,
        }

        resp = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"Pexels error for '{keyword}': {resp.status_code}")
            continue

        videos = resp.json().get("videos", [])

        for video in videos:
            if total_dur >= duration_needed_s:
                break

            # Best quality file choose karo
            video_files = video.get("video_files", [])
            best_file   = _pick_best_file(video_files, orientation)
            if not best_file:
                continue

            clip_path = os.path.join(TEMP_FOOTAGE_DIR, f"{file_id}_clip{clip_index}.mp4")
            success   = _download_file(best_file["link"], clip_path)

            if success:
                clip_dur = video.get("duration", 5)
                clips.append({
                    "path":     clip_path,
                    "duration": clip_dur,
                    "keyword":  keyword,
                    "pexels_id": video.get("id")
                })
                total_dur  += clip_dur
                clip_index += 1

    if not clips:
        raise Exception(f"Koi footage nahi mila keywords ke liye: {keywords}")

    return {
        "clips":          clips,
        "total_duration": total_dur,
        "clips_count":    len(clips)
    }


def _pick_best_file(video_files: list, orientation: str) -> dict:
    """
    Portrait ke liye: 1080x1920 ya smallest height > width
    Landscape ke liye: 1920x1080 ya largest width
    """
    if not video_files:
        return None

    # HD files prefer karo
    hd_files = [f for f in video_files if f.get("quality") in ("hd", "sd") and f.get("link", "").endswith(".mp4")]
    if not hd_files:
        hd_files = [f for f in video_files if f.get("link", "").endswith(".mp4")]

    if not hd_files:
        return None

    if orientation == "portrait":
        # Portrait files prefer karo (h > w)
        portrait = [f for f in hd_files if f.get("height", 0) > f.get("width", 0)]
        if portrait:
            return max(portrait, key=lambda f: f.get("height", 0))
        # Portrait nahi mila — any file
        return hd_files[0]
    else:
        # Landscape — highest resolution
        landscape = [f for f in hd_files if f.get("width", 0) >= f.get("height", 0)]
        if landscape:
            return max(landscape, key=lambda f: f.get("width", 0))
        return hd_files[0]


def _download_file(url: str, save_path: str) -> bool:
    try:
        resp = requests.get(url, stream=True, timeout=60)
        if resp.status_code != 200:
            return False
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Download failed {url}: {e}")
        return False
