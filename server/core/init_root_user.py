import json
from pathlib import Path
from datetime import date

import aiofiles
from server.core.config import settings
from server.core.functions.hash_functions import sha256_hash
from server.core.paths import USERS_DIR

async def init_root_user() -> bool:
    USERS_DIR.mkdir(parents=True, exist_ok=True)

    file_path = USERS_DIR / "root.json"

    # не перезаписываем, если уже есть root
    if file_path.exists():
        return True

    root_user = {
        "password": sha256_hash(text=settings.ROOT_PASSWORD),
        "access": {
            "all": True,
            "insert": True,
            "find": True,
            "update": True,
            "delete": True,
            "create_acc": True,
        },
        "role": "admin",
        "disabled": False,
        "created_at": date.today().isoformat(),
    }

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(root_user, ensure_ascii=False, indent=4))

    return True