from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

LOG_DIR = Path("server") / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _console_handler() -> logging.Handler:
    handler = RichHandler(markup=True, rich_tracebacks=False, show_level=False, show_path=False)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATEFMT))
    return handler


def _file_handler() -> logging.Handler:
    path = LOG_DIR / "server.log"
    handler = RotatingFileHandler(path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATEFMT))
    return handler


def _setup_root_logger() -> logging.Logger:
    root = logging.getLogger()
    root.setLevel(logging.getLevelName(DEFAULT_LEVEL))
    root.handlers.clear()
    root.addHandler(_console_handler())
    root.addHandler(_file_handler())
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    return root


logger = _setup_root_logger().getChild("uav-db")
