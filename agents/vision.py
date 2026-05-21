from google.genai import types

from agents.llm import get_client
from agents.rag import context_block
from agents.settings import MODEL_NAME


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def check_image(image_bytes, mime_type, claim_hint=""):
    if mime_type not in ALLOWED_IMAGE_TYPES:
        return (
            "Verdict: Unverified\n"
            "Reason: Unsupported image type. Upload a JPEG, PNG, or WebP image.\n"
            "Sources: None."
        )

    source_context = context_block(claim_hint or "election voting registration IEBC", limit=6)
    prompt = f"""
You are Ukweli Vision, a neutral election misinformation checker.

Task:
- Inspect the uploaded image.
- Extract any visible election-related claim, poster text, screenshot text, symbol, or instruction.
- Decide exactly one verdict: True, False, Misleading, or Unverified.
- Use Unverified when the image is unclear or the trusted sources do not prove the claim.
- Stay politically neutral. Do not endorse or attack any party, candidate, tribe, or ideology.
- Cite only the trusted source snippets below.
- Do not request, store, or repeat voter ID numbers.

Trusted source snippets:
{source_context}

Optional user hint:
{claim_hint}

Return:
Observed text:
Verdict:
Reason:
Sources:
"""
    fallback = (
        "Observed text: Unclear.\n"
        "Verdict: Unverified\n"
        "Reason: I could not verify the image against trusted civic sources.\n"
        "Sources: IEBC voter education guidance; Constitution of Kenya."
    )

    try:
        response = get_client().models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
        )
        text = (response.text or "").strip()
        return text if text else fallback
    except Exception:
        return fallback
