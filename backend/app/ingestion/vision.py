"""Vision client: extract text/description from an image via a multimodal LLM"""

import base64
import io
from collections.abc import Sequence
from typing import Any

from openai import OpenAI
from PIL import Image

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
        image_bytes, mime = _fit_pixels(image_bytes, mime, settings.vision_max_pixels)
        return _call_vision(image_bytes, mime, settings)
    except Exception as exc:
        logger.warning("Vision call failed, skipping image: %s", exc)
        return None


def _fit_pixels(image_bytes: bytes, mime: str, max_pixels: int) -> tuple[bytes, str]:
    """Downscale an image to the model's pixel budget (e.g. scanned full-page PDFs).

    Returns (bytes, mime). No-op when the image is already within budget or not
    decodable — in the latter case the original bytes are sent and the API call's
    own error handling applies.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            width, height = im.size
            if width * height <= max_pixels:
                return image_bytes, mime
            scale = (max_pixels / (width * height)) ** 0.5
            resized = im.resize((max(1, int(width * scale)), max(1, int(height * scale))))
            if resized.mode not in ("RGB", "L"):
                resized = resized.convert("RGB")
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=85)
            logger.debug("Downscaled image %dx%d to fit %d px budget", width, height, max_pixels)
            return buf.getvalue(), "image/jpeg"
    except Exception as exc:
        logger.debug("Image downscale skipped (%s); sending original", exc)
        return image_bytes, mime


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
