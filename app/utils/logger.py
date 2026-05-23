"""Structured logging configuration."""

import logging
import sys

from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)

    # Atlas may cancel idle pool reconnects; not fatal for the API.
    class _PymongoBackgroundFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if record.name != "pymongo.client":
                return True
            msg = record.getMessage()
            return "background task" not in msg and "_OperationCancelled" not in msg

    for handler in logging.root.handlers:
        handler.addFilter(_PymongoBackgroundFilter())
