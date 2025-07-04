from __future__ import annotations

import json
import logging
from datetime import date, datetime
from pathlib import Path

import aiofiles
from fastapi import Request

from server.core.functions.hash_functions import sha256_hash

try:
    from server.core.paths import LOG_DIR as DEFAULT_LOG_DIR
except ImportError:
    DEFAULT_LOG_DIR = Path.cwd() / "logs"


async def viewing_event(
    request: Request,
    log_dir: Path | None = None,
    verbose: bool = False,
    logger: logging.Logger | None = None,
) -> bool:
    def _say(msg: str) -> None:
        if verbose:
            (logger.info if logger else print)(msg)

    log_dir = log_dir or DEFAULT_LOG_DIR
    _say(f"Log directory resolved to {log_dir}")

    ts = datetime.now().isoformat(timespec="seconds")
    host = request.client.host if request.client else "-"
    port = str(request.client.port) if request.client else "-"

    if hasattr(request.headers, "multi_items"):
        hdr_iter = request.headers.multi_items()
    else:
        hdr_iter = request.headers.items()
    headers_json = json.dumps(list(hdr_iter), ensure_ascii=False)
    _say("Headers serialised")

    _say("Headers serialized to JSON")

    payload = "|".join(map(str, [
        ts,
        request.method,
        host,
        port,
        request.base_url,
        headers_json,
    ]))
    digest = sha256_hash(payload)
    line = f"{payload}|{digest}\n"
    _say("Payload assembled and hashed")

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        _say("Ensured log directory exists")

        log_path = log_dir / f"{date.today():%F}.viewings.logs"
        async with aiofiles.open(log_path, "a", encoding="utf-8") as f:
            await f.write(line)
        _say(f"Wrote one line to {log_path}")

        return True

    except Exception as exc:
        err_msg = f"Ошибка записи лога ({ts}): {exc!s}"
        if logger:
            logger.error(err_msg, exc_info=True)
        else:
            print(err_msg)
        return False
