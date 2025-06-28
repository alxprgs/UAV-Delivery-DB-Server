import jwt 
from jwt import ExpiredSignatureError, InvalidTokenError
from server.core.config import settings
from pathlib import Path
import aiofiles
import json

async def check_user(jwt_token: str) -> bool:
    try:
        payload = jwt.decode(
            jwt_token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require_sub": True, "require_exp": True}
        )
    except ExpiredSignatureError:
        return False, None
    except InvalidTokenError:
        return False, None

    username = payload.get("sub")
    if not username:
        return False, None

    users_file = Path("server") / "core" / "db" / "users.json"
    try:
        async with aiofiles.open(users_file, mode="r", encoding="utf-8") as f:
            content = await f.read()
    except FileNotFoundError:
        return False, None

    try:
        data_json = json.loads(content) if content.strip() else {}
    except json.JSONDecodeError:
        return False, None
    
    user = data_json.get(username)
    if not isinstance(user, dict):
        return False, None
    return True, user