import os
import uuid
import requests
from config import ELEVENLABS_API_KEY, CHANNELS, TEMP_AUDIO_DIR

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

def generate_voice(script: str, channel_key: str, job_id: str = None) -> dict:
    """
    ElevenLabs se MP3 generate karo
    Returns: { "audio_path": str, "duration_estimate_s": int }
    """
    os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

    channel  = CHANNELS[channel_key]
    voice_id = channel["voice_id"]
    lang     = channel["language"]

    # Voice settings — language ke hisaab se tune karo
    voice_settings = {
        "stability":         0.5,
        "similarity_boost":  0.75,
        "style":             0.3,
        "use_speaker_boost": True
    }

    if lang == "hindi":
        # Hindi ke liye thoda slow
        voice_settings["stability"] = 0.6
        voice_settings["style"]     = 0.2

    payload = {
        "text":           script,
        "model_id":       "eleven_multilingual_v2",  # Hindi + English dono support karta hai
        "voice_settings": voice_settings
    }

    headers = {
        "xi-api-key":   ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept":       "audio/mpeg"
    }

    url      = ELEVENLABS_TTS_URL.format(voice_id=voice_id)
    response = requests.post(url, json=payload, headers=headers, timeout=60)

    if response.status_code != 200:
        raise Exception(f"ElevenLabs error {response.status_code}: {response.text[:200]}")

    # Save MP3
    file_id   = job_id or str(uuid.uuid4())[:8]
    audio_path = os.path.join(TEMP_AUDIO_DIR, f"{file_id}_voice.mp3")

    with open(audio_path, "wb") as f:
        f.write(response.content)

    # Duration estimate: ~130 words per minute
    word_count       = len(script.split())
    duration_estimate = int((word_count / 130) * 60)

    return {
        "audio_path":        audio_path,
        "duration_estimate_s": duration_estimate,
        "word_count":        word_count,
        "voice_id":          voice_id
    }


def list_voices() -> list:
    """Available voices check karo"""
    headers  = {"xi-api-key": ELEVENLABS_API_KEY}
    response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)

    if response.status_code != 200:
        raise Exception(f"ElevenLabs voices error: {response.status_code}")

    voices = response.json().get("voices", [])
    return [{"id": v["voice_id"], "name": v["name"]} for v in voices]
