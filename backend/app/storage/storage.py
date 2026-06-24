"""Local filesystem storage for raw uploads"""

import re
import shutil
from pathlib import Path

from app.core.config import get_settings

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]")


def _safe_name(filename: str) -> str:
    """Strip any path components and unsafe chars (anti path traversal)."""
    name = _UNSAFE.sub("_", Path(filename).name)
    return name or "file"


def save_file(document_id: str, filename: str, data: bytes) -> str:
    base = Path(get_settings().upload_dir) / document_id
    base.mkdir(parents=True, exist_ok=True)
    path = base / _safe_name(filename)
    path.write_bytes(data)
    return str(path)


def delete_file(document_id: str) -> None:
    base = Path(get_settings().upload_dir) / document_id
    if base.exists():
        shutil.rmtree(base)
