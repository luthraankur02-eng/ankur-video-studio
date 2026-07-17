<<<<<<< HEAD
# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
=======
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
>>>>>>> 5c44ec80851b8298c1372799d754d6dd9b020679
