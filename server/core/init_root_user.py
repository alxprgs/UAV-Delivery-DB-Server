import json
from pathlib import Path
import aiofiles
from .config import settings
from server.core.functions.hash_functions import sha256_hash

async def init_root_user() -> bool:
    password_hash = sha256_hash(text=settings.ROOT_PASSWORD)

    root_user = {
        "password": password_hash,
        "access": {
            "insert": True,
            "find": True,
            "update": True,
            "delete": True,
            "create_acc": True
        },
    }

    file_path = Path("server") / "core" / "db" / "users.json"

    if not file_path.exists():
        await file_path.parent.mkdir(parents=True, exist_ok=True)
        await aiofiles.open(file_path, mode="w", encoding="utf-8").close()

    async with aiofiles.open(file_path, mode="r+", encoding="utf-8") as f:
        content = await f.read()
        try:
            data = json.loads(content) if content.strip() else {}
        except json.JSONDecodeError:
            backup = file_path.with_suffix(".bak.json")
            await aiofiles.open(backup, mode="w", encoding="utf-8").write(content)
            data = {}

        data["root"] = root_user

        await f.seek(0)
        await f.truncate()
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))

    return True
