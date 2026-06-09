# 🎬 Ankur Video Studio — Phase 1 Backend

Personal video creation tool. Script → Voice → Footage → Video → Upload.

## Channels
| Key | Platform | Language |
|-----|----------|----------|
| `doodle_masti` | YouTube Shorts | Hindi |
| `usmarketpulse` | Instagram Reels | English |
| `india_crypto` | Instagram Reels | Hindi |
| `daily_talks` | YouTube | Hindi |

## Quick Start (Local)

```bash
# 1. Dependencies install karo
pip install -r requirements.txt

# 2. FFmpeg install karo (agar nahi hai)
# Ubuntu: sudo apt install ffmpeg
# Mac: brew install ffmpeg

# 3. .env file banao
cp .env.example .env
# Apni API keys daalo

# 4. Run karo
python main.py
# → http://localhost:8000
# → Docs: http://localhost:8000/docs
```

## API Endpoints

### 1. Script Generate
```bash
curl -X POST http://localhost:8000/generate-script \
  -H "Content-Type: application/json" \
  -d '{"topic": "Bitcoin price today", "channel_key": "india_crypto"}'
```

### 2. Voice Generate
```bash
curl -X POST http://localhost:8000/generate-voice \
  -H "Content-Type: application/json" \
  -d '{"script": "Aaj Bitcoin ne...", "channel_key": "india_crypto", "job_id": "abc123"}'
```

### 3. Full Pipeline (Recommended)
```bash
curl -X POST http://localhost:8000/full-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Top 5 facts about dinosaurs",
    "channel_key": "doodle_masti",
    "auto_upload": false
  }'
# Returns: {"job_id": "abc123", "status": "processing"}

# Status check karo:
curl http://localhost:8000/job/abc123
```

## Railway Deploy

### Step 1: GitHub pe push karo
```bash
git init
git add .
git commit -m "Ankur Video Studio Phase 1"
git remote add origin https://github.com/YOUR_USERNAME/ankur-video-studio.git
git push -u origin main
```

### Step 2: Railway pe new project banao
- railway.app → New Project → Deploy from GitHub
- Repo select karo

### Step 3: Environment Variables set karo
Railway dashboard → Variables mein ye sab daalo:
```
ANTHROPIC_API_KEY=...
ELEVENLABS_API_KEY=...
PEXELS_API_KEY=...
FIREBASE_CRED_JSON={"type":"service_account",...}  ← full JSON paste karo
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_USER_ID=...
EL_VOICE_HINDI_MALE=...
EL_VOICE_ENGLISH_MALE=...
EL_VOICE_KIDS_HINDI=...
```

### Step 4: Deploy!
Railway automatically build + deploy karega.

## ⚠️ Important Notes

**Instagram Upload:**
- Local file upload nahi hota Graph API mein
- Video pehle Firebase Storage ya kisi public URL pe upload karo
- Phir woh URL `/upload-video` endpoint ko do

**YouTube OAuth:**
- Pehle locally OAuth flow complete karo
- `token.json` file banegi — uska content Railway env var mein daalo

**FFmpeg:**
- Dockerfile mein already hai
- Local pe alag se install karna padega

## File Structure
```
ankur-video-studio/
├── main.py              # FastAPI app + all endpoints
├── config.py            # API keys + channel config
├── firebase_client.py   # Job tracking
├── agents/
│   ├── script_agent.py  # Claude API → script
│   ├── voice_agent.py   # ElevenLabs → MP3
│   ├── footage_agent.py # Pexels → video clips
│   ├── video_agent.py   # FFmpeg → final video
│   └── upload_agent.py  # YouTube + Instagram
├── Dockerfile
├── railway.toml
└── requirements.txt
```
