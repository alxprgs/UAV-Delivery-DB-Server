import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

import jwt
import aiofiles
from fastapi import status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server import app
from server.core.config import settings
from server.core.paths import USERS_DIR
from server.core.functions.hash_functions import verify_sha256
from server.core.functions.log_functions import write_log

class DBAuthScheme(BaseModel):
    username: str
    password: str

@app.post("/db/auth/db", status_code=status.HTTP_200_OK, tags=["db"])
async def db_auth(request: Request, data: DBAuthScheme) -> JSONResponse:
    user_file = USERS_DIR / f"{data.username}.json"
    user_data = None
    try:
        async with aiofiles.open(user_file, "r", encoding="utf-8") as f:
            raw = await f.read()
            user_data = json.loads(raw) if raw.strip() else None
    except FileNotFoundError:
        pass

    if not isinstance(user_data, dict):
        await write_log(endpoint="DB auth", request=request, status="Forbidden")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "Неверный логин или пароль."})

    if user_data.get("disabled", False):
        await write_log(endpoint="DB auth", request=request, status="Forbidden")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "Аккаунт заблокирован."})

    if not verify_sha256(text=data.password, expected_hash=user_data.get("password")):
        await write_log(endpoint="DB auth", request=request, status="Forbidden")
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "Неверный логин или пароль."})

    payload = {
        "sub": data.username,
        "role": user_data.get("role", "user"),
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    await write_log(endpoint="DB auth", request=request, status="OK")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "JWT_Token": token})