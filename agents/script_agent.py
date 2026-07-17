import anthropic
from config import ANTHROPIC_API_KEY, CHANNELS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPTS = {
    "hindi": """Tu ek professional Hindi video script writer hai.
Rules:
- Script ONLY Hindi mein likho (Devanagari nahi, Roman/Hinglish OK)
- Engaging, conversational tone
- Short sentences — voice-over ke liye
- No special characters, no emojis
- Sirf bolne wala text — no stage directions, no [MUSIC], no brackets""",

    "english": """You are a professional English video script writer.
Rules:
- Engaging, clear, conversational tone
- Short sentences for voice-over
- No special characters, no emojis
- Only spoken text — no stage directions, no brackets, no [MUSIC]"""
}

def generate_script(topic: str, channel_key: str, custom_script: str = None) -> dict:
    """
    Returns: { "script": str, "title": str, "hashtags": list, "search_keywords": list }
    search_keywords — Pexels footage search ke liye
    """
    if custom_script:
        # User ne khud script di hai — sirf title + keywords extract karo
        return _extract_metadata(custom_script, channel_key)

    channel = CHANNELS[channel_key]
    lang    = channel["language"]
    style   = channel["style"]
    dur     = channel["duration_s"]

    # ~130 words per minute voice-over rate
    word_count = int((dur / 60) * 130)

    user_prompt = f"""Topic: {topic}
Channel style: {style}
Target duration: {dur} seconds (~{word_count} words)

Generate:
1. VIDEO_SCRIPT: The full voice-over script ({word_count} words approx)
2. TITLE: Catchy YouTube/Instagram title
3. HASHTAGS: 5 relevant hashtags (comma separated)
4. KEYWORDS: 3 Pexels stock footage search keywords (comma separated, English only)

Format exactly like:
VIDEO_SCRIPT:
[script here]

TITLE:
[title here]

HASHTAGS:
[hashtags here]

KEYWORDS:
[keywords here]"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPTS[lang],
        messages=[{"role": "user", "content": user_prompt}]
    )

    raw = response.content[0].text
    return _parse_response(raw)


def _parse_response(raw: str) -> dict:
    sections = {"script": "", "title": "", "hashtags": [], "search_keywords": []}

    current = None
    lines = raw.strip().split("\n")
    buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("VIDEO_SCRIPT:"):
            if current and buffer:
                _flush(sections, current, buffer)
            current, buffer = "script", []
        elif stripped.startswith("TITLE:"):
            if current and buffer:
                _flush(sections, current, buffer)
            current, buffer = "title", []
        elif stripped.startswith("HASHTAGS:"):
            if current and buffer:
                _flush(sections, current, buffer)
            current, buffer = "hashtags", []
        elif stripped.startswith("KEYWORDS:"):
            if current and buffer:
                _flush(sections, current, buffer)
            current, buffer = "keywords", []
        elif current and stripped:
            buffer.append(stripped)

    if current and buffer:
        _flush(sections, current, buffer)

    return sections


def _flush(sections, key, buffer):
    text = " ".join(buffer)
    if key == "script":
        sections["script"] = text
    elif key == "title":
        sections["title"] = text
    elif key == "hashtags":
        sections["hashtags"] = [h.strip() for h in text.split(",") if h.strip()]
    elif key == "keywords":
        sections["search_keywords"] = [k.strip() for k in text.split(",") if k.strip()]


def _extract_metadata(custom_script: str, channel_key: str) -> dict:
    """Custom script diya — sirf title aur keywords generate karo"""
    channel = CHANNELS[channel_key]
    lang    = channel["language"]

    prompt = f"""Given this video script, generate:
TITLE: [catchy title]
HASHTAGS: [5 hashtags, comma separated]
KEYWORDS: [3 Pexels search keywords in English, comma separated]

Script:
{custom_script[:500]}"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPTS[lang],
        messages=[{"role": "user", "content": prompt}]
    )

    result = _parse_response(response.content[0].text)
    result["script"] = custom_script
    return result
