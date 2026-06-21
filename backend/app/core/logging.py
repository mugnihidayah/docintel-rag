import json
import logging
import sys
from contextvars import ContextVar

from app.core.config import get_settings

# correlates all log lines within one request
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class ReadableFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return f"[{request_id_var.get()}] {super().format(record)}"


def setup_logging() -> None:
    """COnfigure root logging: structured JSON in prod, human readable in dev"""

    settings = get_settings()
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if settings.is_prod:
        handler.setFormatter(JsonFormatter())
        root.setLevel(logging.INFO)
    else:
        handler.setFormatter(
            ReadableFormatter(
                "%(asctime)s %(levelname)-7s %(name)s — %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        root.setLevel(logging.DEBUG)
    root.addHandler(handler)

    for noisy in ("httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
