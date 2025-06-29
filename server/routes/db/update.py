import json
from pathlib import Path
from typing import Dict, Any, List

import aiofiles
from fastapi import status, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from server import app
from server.core.functions.db_functions import check_user
from server.core.paths import DB_DIR

@app.post("/db/update/{db}/{collection}", status_code=status.HTTP_200_OK, tags=["db"])
async def db_update(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any],
    jwt_token: str = Header(..., alias="JWT_TOKEN")
) -> JSONResponse:
    auth_ok, user = await check_user(jwt_token=jwt_token)
    if not auth_ok:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    if not user.get("access", {}).get("update", False):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "No update permission"})

    filter_ = query.get("filter")
    update_data = query.get("update")
    if not isinstance(filter_, dict) or not isinstance(update_data, dict):
        raise HTTPException(status_code=400, detail="Body must contain 'filter' and 'update' objects")

    collection_dir = DB_DIR / db / collection
    if not collection_dir.exists():
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "updated": 0})

    updated = 0
    async for entry in _iter_dir(collection_dir):
        doc_path = entry
        async with aiofiles.open(doc_path, "r", encoding="utf-8") as f:
            raw = await f.read()
            doc = json.loads(raw)

        if all(doc.get(k) == v for k, v in filter_.items()):
            doc.update(update_data)
            async with aiofiles.open(doc_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(doc, ensure_ascii=False, indent=4))
            updated += 1

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "updated": updated})

async def _iter_dir(dir_path: Path):
    for item in dir_path.glob("*.json"):
        yield item