import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from agents.script_agent  import generate_script
from agents.voice_agent   import generate_voice, list_voices
from agents.footage_agent import fetch_footage
from agents.video_agent   import assemble_video
from agents.upload_agent  import upload_youtube, upload_instagram
from firebase_client      import create_job, update_job, get_job
from config               import CHANNELS

app = FastAPI(
    title       = "Ankur Video Studio API",
    description = "Personal video creation tool — Doodle Masti / USMarketPulse / India Crypto / Daily Talks",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────

class ScriptRequest(BaseModel):
    topic:         str
    channel_key:   str   # doodle_masti / usmarketpulse / india_crypto / daily_talks
    custom_script: Optional[str] = None

class VoiceRequest(BaseModel):
    script:      str
    channel_key: str
    job_id:      Optional[str] = None

class FootageRequest(BaseModel):
    keywords:    List[str]
    duration_s:  int
    channel_key: str
    job_id:      Optional[str] = None

class AssembleRequest(BaseModel):
    job_id:      str
    script:      str
    title:       str
    channel_key: str

class UploadRequest(BaseModel):
    job_id:          str
    platform:        str   # youtube / instagram
    title:           str
    description:     str
    hashtags:        List[str]
    channel_key:     str
    yt_credentials:  Optional[str] = None   # YouTube OAuth JSON
    ig_video_url:    Optional[str] = None   # Instagram requires public URL
    ig_user_id:      Optional[str] = None

class FullPipelineRequest(BaseModel):
    topic:         str
    channel_key:   str
    custom_script: Optional[str] = None
    auto_upload:   bool = False
    yt_credentials: Optional[str] = None


# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status":   "running",
        "service":  "Ankur Video Studio",
        "channels": list(CHANNELS.keys()),
        "endpoints": [
            "POST /generate-script",
            "POST /generate-voice",
            "POST /fetch-footage",
            "POST /assemble-video",
            "POST /upload-video",
            "POST /full-pipeline",
            "GET  /job/{job_id}",
            "GET  /voices",
            "GET  /channels"
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/channels")
def get_channels():
    return CHANNELS

@app.get("/voices")
def get_voices():
    try:
        return {"voices": list_voices()}
    except Exception as e:
        raise HTTPException(500, str(e))


# ─────────────────────────────────────────────
# STEP 1: GENERATE SCRIPT
# ─────────────────────────────────────────────

@app.post("/generate-script")
def api_generate_script(req: ScriptRequest):
    """
    Topic do → Claude se script generate karo.
    Custom script doge to sirf title + keywords extract karega.
    """
    if req.channel_key not in CHANNELS:
        raise HTTPException(400, f"Invalid channel. Available: {list(CHANNELS.keys())}")

    try:
        result = generate_script(
            topic         = req.topic,
            channel_key   = req.channel_key,
            custom_script = req.custom_script
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(500, f"Script generation failed: {str(e)}")


# ─────────────────────────────────────────────
# STEP 2: GENERATE VOICE
# ─────────────────────────────────────────────

@app.post("/generate-voice")
def api_generate_voice(req: VoiceRequest):
    """Script do → ElevenLabs se MP3 banao"""
    if req.channel_key not in CHANNELS:
        raise HTTPException(400, f"Invalid channel: {req.channel_key}")

    try:
        result = generate_voice(
            script      = req.script,
            channel_key = req.channel_key,
            job_id      = req.job_id
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(500, f"Voice generation failed: {str(e)}")


# ─────────────────────────────────────────────
# STEP 3: FETCH FOOTAGE
# ─────────────────────────────────────────────

@app.post("/fetch-footage")
def api_fetch_footage(req: FootageRequest):
    """Keywords do → Pexels se clips download karo"""
    if req.channel_key not in CHANNELS:
        raise HTTPException(400, f"Invalid channel: {req.channel_key}")

    channel     = CHANNELS[req.channel_key]
    orientation = "portrait" if "1920" in channel["resolution"].split("x")[1] else "landscape"

    try:
        result = fetch_footage(
            keywords         = req.keywords,
            duration_needed_s = req.duration_s,
            orientation      = orientation,
            job_id           = req.job_id
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(500, f"Footage fetch failed: {str(e)}")


# ─────────────────────────────────────────────
# STEP 4: ASSEMBLE VIDEO
# ─────────────────────────────────────────────

@app.post("/assemble-video")
def api_assemble_video(req: AssembleRequest):
    """Voice + footage + subtitles → final MP4"""
    import glob

    job_id = req.job_id

    # Files dhundo job_id ke hisaab se
    audio_files = glob.glob(f"temp/audio/{job_id}_voice.mp3")
    clip_files  = sorted(glob.glob(f"temp/footage/{job_id}_clip*.mp4"))

    if not audio_files:
        raise HTTPException(400, f"Audio file nahi mili job_id: {job_id}")
    if not clip_files:
        raise HTTPException(400, f"Footage clips nahi mile job_id: {job_id}")

    audio_path = audio_files[0]
    clips = [{"path": f, "duration": 5} for f in clip_files]  # duration approximate

    try:
        result = assemble_video(
            clips       = clips,
            audio_path  = audio_path,
            script      = req.script,
            title       = req.title,
            channel_key = req.channel_key,
            job_id      = job_id
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(500, f"Video assembly failed: {str(e)}")


# ─────────────────────────────────────────────
# STEP 5: UPLOAD VIDEO
# ─────────────────────────────────────────────

@app.post("/upload-video")
def api_upload_video(req: UploadRequest):
    """Final video YouTube ya Instagram pe upload karo"""
    import glob

    # Video file dhundo
    video_files = glob.glob(f"temp/output/{req.job_id}_final.mp4")
    if not video_files:
        raise HTTPException(400, f"Video file nahi mili job_id: {req.job_id}")

    video_path = video_files[0]

    try:
        if req.platform == "youtube":
            result = upload_youtube(
                video_path       = video_path,
                title            = req.title,
                description      = req.description,
                hashtags         = req.hashtags,
                channel_key      = req.channel_key,
                credentials_json = req.yt_credentials
            )
        elif req.platform == "instagram":
            if not req.ig_video_url:
                raise HTTPException(400, "Instagram ke liye ig_video_url chahiye (public URL)")
            result = upload_instagram(
                video_path   = req.ig_video_url,
                caption      = req.description,
                hashtags     = req.hashtags,
                ig_user_id   = req.ig_user_id
            )
        else:
            raise HTTPException(400, f"Invalid platform: {req.platform}. Use 'youtube' or 'instagram'")

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")


# ─────────────────────────────────────────────
# FULL PIPELINE (Background Job)
# ─────────────────────────────────────────────

@app.post("/full-pipeline")
def api_full_pipeline(req: FullPipelineRequest, background_tasks: BackgroundTasks):
    """
    Ek request mein poora pipeline:
    Script → Voice → Footage → Assembly → (optional) Upload
    Job ID return karta hai turant, processing background mein hoti hai.
    """
    if req.channel_key not in CHANNELS:
        raise HTTPException(400, f"Invalid channel: {req.channel_key}")

    job_id = create_job(req.channel_key, req.topic)

    background_tasks.add_task(
        _run_pipeline,
        job_id         = job_id,
        topic          = req.topic,
        channel_key    = req.channel_key,
        custom_script  = req.custom_script,
        auto_upload    = req.auto_upload,
        yt_credentials = req.yt_credentials
    )

    return {
        "success":     True,
        "job_id":      job_id,
        "status":      "processing",
        "check_status": f"/job/{job_id}"
    }


async def _run_pipeline(job_id, topic, channel_key, custom_script, auto_upload, yt_credentials):
    channel = CHANNELS[channel_key]

    try:
        # Step 1: Script
        update_job(job_id, "running", "script", {"status": "started"})
        script_data = generate_script(topic, channel_key, custom_script)
        update_job(job_id, "running", "script", {
            "status": "done",
            "title":  script_data["title"],
            "words":  len(script_data["script"].split())
        })

        # Step 2: Voice
        update_job(job_id, "running", "voice", {"status": "started"})
        voice_data = generate_voice(script_data["script"], channel_key, job_id)
        update_job(job_id, "running", "voice", {
            "status":   "done",
            "duration": voice_data["duration_estimate_s"]
        })

        # Step 3: Footage
        update_job(job_id, "running", "footage", {"status": "started"})
        orientation = "portrait" if "1920" in channel["resolution"].split("x")[1] else "landscape"
        footage_data = fetch_footage(
            script_data["search_keywords"],
            voice_data["duration_estimate_s"] + 5,
            orientation,
            job_id
        )
        update_job(job_id, "running", "footage", {
            "status": "done",
            "clips":  footage_data["clips_count"]
        })

        # Step 4: Assemble
        update_job(job_id, "running", "assembly", {"status": "started"})
        video_data = assemble_video(
            clips       = footage_data["clips"],
            audio_path  = voice_data["audio_path"],
            script      = script_data["script"],
            title       = script_data["title"],
            channel_key = channel_key,
            job_id      = job_id
        )
        update_job(job_id, "running", "assembly", {
            "status":     "done",
            "video_path": video_data["video_path"],
            "duration":   video_data["duration"]
        })

        # Step 5: Upload (optional)
        if auto_upload and channel["platform"] == "youtube" and yt_credentials:
            update_job(job_id, "running", "upload", {"status": "started"})
            upload_result = upload_youtube(
                video_path       = video_data["video_path"],
                title            = script_data["title"],
                description      = script_data["script"][:300] + "...",
                hashtags         = script_data["hashtags"],
                channel_key      = channel_key,
                credentials_json = yt_credentials
            )
            update_job(job_id, "completed", "upload", {
                "status":   "done",
                "url":      upload_result["url"],
                "video_id": upload_result["video_id"]
            })
        else:
            update_job(job_id, "completed", "final", {
                "video_path":  video_data["video_path"],
                "title":       script_data["title"],
                "hashtags":    script_data["hashtags"],
                "ready_to_upload": True
            })

    except Exception as e:
        update_job(job_id, "failed", "error", {"message": str(e)})
        print(f"Pipeline failed for job {job_id}: {e}")


# ─────────────────────────────────────────────
# JOB STATUS
# ─────────────────────────────────────────────

@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    return get_job(job_id)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
