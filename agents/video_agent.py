import os
import uuid
import subprocess
import json
from config import CHANNELS, TEMP_OUTPUT_DIR

def assemble_video(
    clips: list,
    audio_path: str,
    script: str,
    title: str,
    channel_key: str,
    job_id: str = None
) -> dict:
    """
    FFmpeg se final video assemble karo:
    - Clips ko trim + loop karo audio duration tak
    - Audio mix karo
    - Subtitles add karo (SRT format)
    - Title overlay add karo
    Returns: { "video_path": str, "duration": float }
    """
    os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)

    channel    = CHANNELS[channel_key]
    resolution = channel["resolution"]
    file_id    = job_id or str(uuid.uuid4())[:8]

    w, h = resolution.split("x")
    w, h = int(w), int(h)

    # Step 1: Audio duration nikalo
    audio_duration = _get_duration(audio_path)
    if not audio_duration:
        raise Exception(f"Audio duration nahi mila: {audio_path}")

    # Step 2: Clips list banao jab tak audio cover na ho
    extended_clips = _extend_clips(clips, audio_duration)

    # Step 3: Clips ko resize + concatenate karo
    concat_path = os.path.join(TEMP_OUTPUT_DIR, f"{file_id}_concat.mp4")
    _concat_clips(extended_clips, concat_path, w, h)

    # Step 4: SRT subtitle file banao
    srt_path = _generate_srt(script, audio_duration, file_id)

    # Step 5: Final assembly — concat + audio + subtitles + title
    output_path = os.path.join(TEMP_OUTPUT_DIR, f"{file_id}_final.mp4")
    _final_assembly(concat_path, audio_path, srt_path, title, output_path, w, h, audio_duration)

    final_duration = _get_duration(output_path)

    # Cleanup intermediate files
    _cleanup([concat_path, srt_path])

    return {
        "video_path": output_path,
        "duration":   final_duration,
        "resolution": resolution,
        "job_id":     file_id
    }


def _get_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception:
        return None


def _extend_clips(clips: list, needed_duration: float) -> list:
    """Clips ko repeat karo jab tak needed_duration cover na ho"""
    extended = []
    total    = 0
    i        = 0
    while total < needed_duration:
        clip = clips[i % len(clips)]
        extended.append(clip)
        total += clip["duration"]
        i     += 1
    return extended


def _concat_clips(clips: list, output_path: str, w: int, h: int):
    """Clips ko resize karke ek file mein join karo"""
    inputs   = []
    filters  = []
    n        = len(clips)

    for i, clip in enumerate(clips):
        inputs += ["-i", clip["path"]]
        # Crop to fill (no black bars), then scale
        filters.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},setsar=1,fps=30[v{i}]"
        )

    concat_input = "".join([f"[v{i}]" for i in range(n)])
    filters.append(f"{concat_input}concat=n={n}:v=1:a=0[outv]")

    filter_complex = ";".join(filters)

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + [
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
    )

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg concat failed:\n{result.stderr[-500:]}")


def _generate_srt(script: str, duration: float, file_id: str) -> str:
    """Simple SRT — words ko evenly distribute karo duration mein"""
    words     = script.split()
    if not words:
        return ""

    srt_path  = os.path.join(TEMP_OUTPUT_DIR, f"{file_id}.srt")
    # ~5 words per subtitle block
    chunk_size = 5
    chunks     = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
    n          = len(chunks)
    time_per   = duration / n

    lines = []
    for idx, chunk in enumerate(chunks):
        start_s = idx * time_per
        end_s   = (idx + 1) * time_per
        lines.append(str(idx + 1))
        lines.append(f"{_fmt_time(start_s)} --> {_fmt_time(end_s)}")
        lines.append(" ".join(chunk))
        lines.append("")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return srt_path


def _fmt_time(seconds: float) -> str:
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def _final_assembly(
    video_path: str,
    audio_path: str,
    srt_path: str,
    title: str,
    output_path: str,
    w: int, h: int,
    duration: float
):
    """Final video: video + audio + subtitles + title text"""
    font_size_sub   = max(24, h // 30)
    font_size_title = max(32, h // 22)
    safe_title      = title.replace("'", "\\'").replace(":", "\\:")[:60]

    # Subtitle filter — bottom center, white with black outline
    sub_filter = (
        f"subtitles={srt_path}:force_style='"
        f"FontSize={font_size_sub},"
        f"PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"Outline=2,"
        f"Alignment=2,"
        f"MarginV=60'"
    )

    # Title overlay — top, first 3 seconds only
    title_filter = (
        f"drawtext=text='{safe_title}':"
        f"fontsize={font_size_title}:"
        f"fontcolor=white:"
        f"x=(w-text_w)/2:"
        f"y=80:"
        f"box=1:boxcolor=black@0.5:boxborderw=10:"
        f"enable='between(t,0,3)'"
    )

    filter_complex = f"{sub_filter},{title_filter}"

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-t", str(duration),
        "-movflags", "+faststart",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg final assembly failed:\n{result.stderr[-500:]}")


def _cleanup(files: list):
    for f in files:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except Exception:
            pass
