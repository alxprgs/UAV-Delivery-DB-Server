from pathlib import Path
from datetime import datetime, timedelta
import json, jwt, aiofiles

from fastapi import status, Request, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server import app
from server.core.config import settings
from server.core.functions.hash_functions import verify_sha256
from server.core.functions.log_functions import write_log
from server.events.viewing_event import viewing_event

class DBAuthScheme(BaseModel):
    username: str
    password: str

@app.post(
    "/db/auth/db",
    status_code=status.HTTP_200_OK,
    tags=["db"],
)
async def db_auth(
    request: Request,
    data: DBAuthScheme = Body(
        ...,
        openapi_examples={
            "root": {
                "summary": "Войти под root",
                "value": {"username": "root", "password": "<ROOT_PASSWORD>"},
            },
            "user": {
                "summary": "Войти под обычным пользователем",
                "value": {"username": "user1", "password": "<USER_PASSWORD>"},
            },
        },
    ),
) -> JSONResponse:
    await viewing_event(request)
    users_file = Path("server/core/db_files/users.json")

    async with aiofiles.open(users_file, "r", encoding="utf-8") as f:
        raw = await f.read()
    data_json = json.loads(raw) if raw.strip() else {}

    user = data_json.get(data.username)
    if not isinstance(user, dict) or not verify_sha256(data.password, user.get("password", "")):
        await write_log(endpoint="DB auth", request=request, status="Forbidden")
        return JSONResponse(status_code=403, content={"status": False, "message": "Неверный логин или пароль."})

    payload = {
        "sub": data.username,
        "role": user.get("access", {}).get("role", "user"),
        "exp": datetime.now() + timedelta(hours=24),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    await write_log(endpoint="DB auth", request=request, status="OK")
    return JSONResponse(status_code=200, content={"status": True, "JWT_Token": token})
