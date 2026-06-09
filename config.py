import os
from dotenv import load_dotenv

load_dotenv()

# ─── API Keys ───────────────────────────────────────────────
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY", "")
PEXELS_API_KEY      = os.getenv("PEXELS_API_KEY", "")
FIREBASE_CRED_PATH  = os.getenv("FIREBASE_CRED_PATH", "firebase_cred.json")

# ─── YouTube OAuth (one per channel) ────────────────────────
YT_CLIENT_SECRET_PATH = os.getenv("YT_CLIENT_SECRET_PATH", "yt_client_secret.json")

# ─── Instagram Graph API ─────────────────────────────────────
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

# ─── ElevenLabs Voice IDs ────────────────────────────────────
# Get voice IDs from: https://api.elevenlabs.io/v1/voices
VOICE_IDS = {
    "hindi_male":   os.getenv("EL_VOICE_HINDI_MALE",   "pNInz6obpgDQGcFmaJgB"),  # replace with your voice
    "english_male": os.getenv("EL_VOICE_ENGLISH_MALE", "21m00Tcm4TlvDq8ikWAM"),
    "kids_hindi":   os.getenv("EL_VOICE_KIDS_HINDI",   "AZnzlk1XvdvUeBnXmlld"),
}

# ─── Channel Config ──────────────────────────────────────────
CHANNELS = {
    "doodle_masti": {
        "name":        "Doodle Masti",
        "platform":    "youtube",
        "language":    "hindi",
        "voice_id":    VOICE_IDS["kids_hindi"],
        "style":       "fun, kids, short, animated energy",
        "duration_s":  55,   # YouTube Shorts < 60s
        "resolution":  "1080x1920",  # vertical
    },
    "usmarketpulse": {
        "name":        "USMarketPulse",
        "platform":    "instagram",
        "language":    "english",
        "voice_id":    VOICE_IDS["english_male"],
        "style":       "professional, finance, US market news",
        "duration_s":  30,
        "resolution":  "1080x1920",
    },
    "india_crypto": {
        "name":        "India Crypto",
        "platform":    "instagram",
        "language":    "hindi",
        "voice_id":    VOICE_IDS["hindi_male"],
        "style":       "crypto news Hindi, energetic, informative",
        "duration_s":  30,
        "resolution":  "1080x1920",
    },
    "daily_talks": {
        "name":        "Daily Talks by Ankur",
        "platform":    "youtube",
        "language":    "hindi",
        "voice_id":    VOICE_IDS["hindi_male"],
        "style":       "geopolitics, right-wing commentary, analytical",
        "duration_s":  60,
        "resolution":  "1920x1080",  # landscape for long-form
    },
}

# ─── Paths ───────────────────────────────────────────────────
TEMP_FOOTAGE_DIR = "temp/footage"
TEMP_AUDIO_DIR   = "temp/audio"
TEMP_OUTPUT_DIR  = "temp/output"
