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
from server.core.api.schemes.SpecializedDBRfidCardcheckScheme import SpecializedDBRfidCardcheckScheme

@app.post("/db/specialized/check/card")
async def specialized_db_rfid_card_check(request: Request, data: SpecializedDBRfidCardcheckScheme):
    await viewing_event(request)