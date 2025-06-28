import json
from pathlib import Path
from datetime import datetime, timedelta

import jwt
from fastapi import status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles

from server import app
from server.core.config import settings
from server.core.functions.hash_functions import verify_sha256
from server.core.functions.log_functions import write_log

class DBAuthScheme(BaseModel):
    username: str
    password: str

@app.post("/db/auth", status_code=status.HTTP_200_OK, tags=["db"])
async def db_auth(request: Request, data: DBAuthScheme) -> JSONResponse:
    users_file = Path("server/core/db_files/users.json")

    try:
        async with aiofiles.open(users_file, mode="r", encoding="utf-8") as f:
            raw = await f.read()
    except FileNotFoundError:
        await write_log(endpoint="DB auth", request=request, status="Internal Server Error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "message": "Сервис временно недоступен."}
        )

    try:
        data_json = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        await write_log(endpoint="DB auth", request=request, status="Internal Server Error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "message": "Неправильный формат файла пользователей."}
        )

    user = data_json.get(data.username)
    if not isinstance(user, dict):
        await write_log(endpoint="DB auth", request=request, status="Forbidden")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": False, "message": "Неверный логин или пароль."}
        )

    stored_hash = user.get("password", "")
    if not verify_sha256(text=data.password, expected_hash=stored_hash):
        await write_log(endpoint="DB auth", request=request, status="Forbidden")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": False, "message": "Неверный логин или пароль."}
        )

    payload = {
        "sub": data.username,
        "role": user.get("access", {}).get("role", "user"),
        "exp": datetime.now() + timedelta(hours=24)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    await write_log(endpoint="DB auth", request=request, status="OK")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": True, "JWT_Token": token}
    )
