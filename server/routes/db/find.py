import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import status, Request, HTTPException, Header, Query
from fastapi.responses import JSONResponse

from server import app
from server.core.functions.db_functions import check_user, _load_json as load_json
from server.core.paths import DB_DIR

@app.post("/db/find/{db}/{collection}", status_code=status.HTTP_200_OK, tags=["db"])
async def db_find(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any],
    jwt_token: str = Header(..., alias="JWT_TOKEN"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    sort: Optional[str] = Query(None, description="field:asc|desc")
) -> JSONResponse:
    auth_ok, user = await check_user(jwt_token=jwt_token)
    if not auth_ok:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    if not user.get("access", {}).get("find", False):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "No find permission"})

    collection_dir = DB_DIR / db / collection
    if not collection_dir.exists():
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "total": 0, "data": []})

    docs: List[Dict[str, Any]] = []
    for path in collection_dir.glob("*.json"):
        doc = await load_json(path)
        if doc is None:
            continue
        if all(doc.get(k) == v for k, v in query.items()):
            docs.append(doc)

    if sort:
        field, _, direction = sort.partition(":")
        reverse = direction.lower() == "desc"
        try:
            docs.sort(key=lambda d: d.get(field), reverse=reverse)
        except TypeError:
            pass

    total = len(docs)
    paginated = docs[skip: skip + limit]

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "total": total, "skip": skip, "limit": limit, "data": paginated})