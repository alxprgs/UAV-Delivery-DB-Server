import json
from datetime import date
import aiofiles
from secrets import token_urlsafe

from server.core.config import settings
from server.core.paths import WORKERS_DIR

async def init_ceo_worker() -> bool:
    WORKERS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = WORKERS_DIR / f"{settings.CEO_NAME}_{settings.CEO_SURNAME}.json"

    if file_path.exists():
            return True

    ceo_worker = {
        "name": settings.CEO_NAME,
        "surname": settings.CEO_SURNAME,
        "post": "CEO",
        "mail": f"ceo@{settings.BASE_DOMAIN}",
        "access": {
            "all": True
        },
        "disabled": False,
        "created_at": date.today().isoformat(),
        "cardid": token_urlsafe(32)
    }

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(ceo_worker, ensure_ascii=False, indent=4))

    return True