"""Vision client: extract text/description from an image via a multimodal LLM"""

import base64
from collections.abc import Sequence
from typing import Any

from openai import OpenAI

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.ingestion.models import Element, ElementType, Location

logger = get_logger(__name__)

_PROMPT = (
    "Extract all readable text from this image verbatim. "
    "If it is a chart, diagram, or screenshot, also add a short factual description "
    "of what it shows. Reply with plain text only, no preamble."
)


def describe_image(image_bytes: bytes, mime: str) -> str | None:
    """return text of an image or None if disabled, too small, or failed"""

    settings = get_settings()
    if not settings.vision_enabled or not settings.vision_key:
        return None
    if len(image_bytes) < settings.vision_min_image_kb * 1024:
        return None
    try:
        return _call_vision(image_bytes, mime, settings)
    except Exception as exc:
        logger.warning("Vision call failed, skipping image: %s", exc)
        return None


def _call_vision(image_bytes: bytes, mime: str, settings: Settings) -> str:
    b64 = base64.b64encode(image_bytes).decode("ascii")
    client = OpenAI(
        base_url=settings.vision_base_url,
        api_key=settings.vision_key,
        timeout=settings.vision_timeout_s,
    )
    messages: Any = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": _PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }
    ]
    resp = client.chat.completions.create(
        model=settings.vision_model, temperature=0, messages=messages
    )
    return (resp.choices[0].message.content or "").strip()


def images_to_elements(images: Sequence[tuple[bytes, str, Location]]) -> list[Element]:
    """Run vision on images (size-filtered + per-document capped) -> IMAGE elements."""
    settings = get_settings()
    big = [img for img in images if len(img[0]) >= settings.vision_min_image_kb * 1024]
    out: list[Element] = []
    for blob, mime, location in big[: settings.vision_max_images]:
        desc = describe_image(blob, mime)
        if desc:
            out.append(Element(text=desc, element_type=ElementType.IMAGE, location=location))
    return out
