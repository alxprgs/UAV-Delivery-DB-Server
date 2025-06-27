from fastapi import Request
from pathlib import Path
from datetime import datetime, date
from .hash_functions import sha256_hash
import aiofiles

LOG_DIR = Path("server") / "logs"

async def write_log(endpoint: str, request: Request, log_dir: Path = LOG_DIR, status: str ="OK") -> bool:
    timestamp = datetime.now().isoformat()
    parts = [timestamp, endpoint, request.method, request.client.host, status]
    payload = "|".join(parts)
    digest = sha256_hash(payload)
    log_line = f"{payload}|{digest}\n"

    log_path = log_dir / f"{date.today().isoformat()}.logs"
    try:
        async with aiofiles.open(log_path, "a", encoding="utf-8") as f:
            await f.write(log_line)
        return True
    except Exception as e:
        print(f"Ошибка записи лога: {e}, {timestamp}")
        return False
