import os
import json
import uuid
from datetime import datetime

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from config import FIREBASE_CRED_PATH

_db = None

def _get_db():
    global _db
    if _db:
        return _db

    if not FIREBASE_AVAILABLE:
        return None

    cred_path = FIREBASE_CRED_PATH

    # Railway pe env var se JSON string bhi ho sakta hai
    cred_json = os.getenv("FIREBASE_CRED_JSON")
    if cred_json:
        cred_data = json.loads(cred_json)
        cred = credentials.Certificate(cred_data)
    elif os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        print("Firebase credentials nahi mili — job tracking disabled")
        return None

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def create_job(channel_key: str, topic: str) -> str:
    """Naya job create karo, job_id return karo"""
    job_id = str(uuid.uuid4())[:8]
    job = {
        "job_id":     job_id,
        "channel":    channel_key,
        "topic":      topic,
        "status":     "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "steps":      {}
    }

    db = _get_db()
    if db:
        db.collection("video_jobs").document(job_id).set(job)

    print(f"Job created: {job_id}")
    return job_id


def update_job(job_id: str, status: str, step: str = None, data: dict = None):
    """Job status update karo"""
    update = {
        "status":     status,
        "updated_at": datetime.utcnow().isoformat()
    }

    if step and data:
        update[f"steps.{step}"] = data

    db = _get_db()
    if db:
        db.collection("video_jobs").document(job_id).update(update)

    print(f"Job {job_id} → {status}" + (f" [{step}]" if step else ""))


def get_job(job_id: str) -> dict:
    """Job details fetch karo"""
    db = _get_db()
    if not db:
        return {"job_id": job_id, "status": "unknown", "note": "Firebase not connected"}

    doc = db.collection("video_jobs").document(job_id).get()
    if doc.exists:
        return doc.to_dict()
    return {"job_id": job_id, "status": "not_found"}
