from server import app
from server.core.config import settings
from fastapi import status, Request
import jwt

@app.get("/db/auth/card")
async def card_auth(guard_code):
    pass