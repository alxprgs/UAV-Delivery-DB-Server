import jwt 
from datetime import datetime, timezone
from server.core.config import settings
from server.core.paths import USERS_DIR
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
import aiofiles
import json
from enum import Enum

class Principal(str, Enum):
    user = "user"
    worker = "worker"

async def open_json(path: Path) -> Dict[str, Any]:
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            raw = await f.read()
    except FileNotFoundError:
        return {}
    try:
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


async def _load_json(path: Path) -> Any:
    try:
        async with aiofiles.open(path, mode="r", encoding="utf-8") as f:
            raw = await f.read()
            return json.loads(raw) if raw.strip() else None
    except FileNotFoundError:
        return None

async def get_user(username: str) -> Optional[Dict[str, Any]]:
    path = USERS_DIR / f"{username}.json"
    return await _load_json(path)

async def check_user(jwt_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    try:
        payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"], options={"require_sub": True, "require_exp": True})
    except jwt.ExpiredSignatureError:
        return False, None
    except jwt.PyJWTError:
        return False, None

    username = payload.get("sub")
    if not username:
        return False, None

    user = await get_user(username)
    if not user or user.get("disabled", False):
        return False, None

    if payload.get("exp", 0) < datetime.now(tz=timezone.utc).timestamp():
        return False, None

    return True, user

def parse_sort_param(sort: Optional[str]) -> Optional[Tuple[str, bool]]:
    if not sort:
        return None
    try:
        field, direction = sort.split(":", 1)
        reverse = direction.lower() == "desc"
        return field, reverse
    except ValueError:
        return None