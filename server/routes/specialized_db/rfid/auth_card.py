from server import app
from server.core.config import settings
from fastapi import Request, HTTPException, status, Body
from fastapi.responses import JSONResponse
from server.core.functions.security_functions import banned
from server.core.paths import WORKERS_DIR
from server.core.functions.db_functions import open_json
from datetime import datetime, timedelta
import jwt
from server.events.viewing_event import viewing_event

TTL = timedelta(minutes=30)

@app.post("/db/auth/card")
async def card_auth(request: Request, guard_code: str = Body(...), cardid: str = Body(...)):
    await viewing_event(request)
    ip = request.headers.get("X-Forwarded-For", request.client.host).split(',')[0].strip()
    if banned(ip):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "IP заблокирован на 30 минут")
    if guard_code != settings.SECURITY_ACCESS_CODE:
        app.state.blocked[ip] = datetime.utcnow() + TTL
        return JSONResponse(content={"status": False, "message": "Неверный код доступа охраны, IP заблокирован на 30 минут"})
    
    user = post = None
    for worker_path in WORKERS_DIR.glob("*.json"):
        data = await open_json(worker_path)
        if data.get("cardid") == cardid:
            user, post = data["name"], data["post"]
            break

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Карта не найдена")

    payload = {
        "sub": user,
        "role": post,
        "exp": datetime.now() + timedelta(hours=18),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "Token": token})
