import json
import uuid
from pathlib import Path
from typing import Dict, Any

import aiofiles
from fastapi import status, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from server import app
from server.core.functions.db_functions import check_user
from server.core.paths import DB_DIR

@app.post("/db/insert/{db}/{collection}", status_code=status.HTTP_201_CREATED, tags=["db"])
async def db_insert(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any],
    jwt_token: str = Header(..., alias="JWT_TOKEN")
) -> JSONResponse:
    auth_ok, user = await check_user(jwt_token=jwt_token)
    if not auth_ok:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    if not user.get("access", {}).get("insert", False):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "No insert permission"})

    if not isinstance(query, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")

    collection_dir = DB_DIR / db / collection
    collection_dir.mkdir(parents=True, exist_ok=True)

    while True:
        doc_id = uuid.uuid4().hex
        file_path = collection_dir / f"{doc_id}.json"
        if not file_path.exists():
            break

    doc = {"id": doc_id, **query}

    async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
        await f.write(json.dumps(doc, ensure_ascii=False, indent=4))

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status": True, "data": doc})