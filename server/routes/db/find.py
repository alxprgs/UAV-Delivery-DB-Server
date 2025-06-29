import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import status, Request, Depends, Body, Query
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.core.security import require_access

@app.post(
    "/db/find/{db}/{collection}",
    status_code=status.HTTP_200_OK,
    tags=["db"],
)
async def db_find(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any] = Body(
        default={},
        examples={
            "by_name": {
                "summary": "Фильтр по имени",
                "value": {"name": "Battery 4S"},
            },
            "empty": {
                "summary": "Без фильтра (вернуть все документы)",
                "value": {},
            },
        },
    ),
    user: Dict = Depends(require_access("find")),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    sort: Optional[str] = Query(None, description="field:asc|desc"),
):
    collection_dir = DB_DIR / db / collection
    if not collection_dir.exists():
        return JSONResponse(status_code=200, content={"status": True, "total": 0, "data": []})

    docs: List[Dict[str, Any]] = []
    for path in collection_dir.glob("*.json"):
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            doc = json.loads(await f.read())
        if all(doc.get(k) == v for k, v in query.items()):
            docs.append(doc)

    if sort:
        field, _, direction = sort.partition(":")
        reverse = direction.lower() == "desc"
        try:
            docs.sort(key=lambda d: d.get(field), reverse=reverse)
        except TypeError:
            pass

    return JSONResponse(
        status_code=200,
        content={
            "status": True,
            "total": len(docs),
            "data": docs[skip : skip + limit],
        },
    )
