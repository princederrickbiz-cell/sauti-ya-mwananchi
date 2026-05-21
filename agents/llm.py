from google import genai

from agents.settings import (
    GEMINI_API_KEY,
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_CLOUD_PROJECT,
    MODEL_NAME,
)


_client = None


def get_client():
    global _client
    if _client is not None:
        return _client

    if GOOGLE_CLOUD_PROJECT:
        _client = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION,
        )
    elif GEMINI_API_KEY:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        raise RuntimeError(
            "Add GEMINI_API_KEY=your_key_here or GOOGLE_CLOUD_PROJECT=your-project to .env"
        )

    return _client


def generate(prompt, fallback):
    """Call Gemini, but keep user-facing replies clean if credentials are not ready."""
    try:
        response = get_client().models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        text = (response.text or "").strip()
        return text if text else fallback
    except Exception:
        return fallback
