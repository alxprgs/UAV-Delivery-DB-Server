import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import status, Request, Depends
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.core.security import require_access
from server.events.viewing_event import viewing_event
from server.core.api.schemes.DBFindScheme import DBFindScheme

@app.post(
    "/db/base/find/{db}/{collection}",
    status_code=status.HTTP_200_OK,
    tags=["db"],
)
async def db_find(
    request: Request,
    data: DBFindScheme,
    user: dict = Depends(require_access("find"))
):
    await viewing_event(request)
    collection_dir = DB_DIR / data.db / data.collection
    if not collection_dir.exists():
        return JSONResponse(status_code=200, content={"status": True, "total": 0, "data": []})

    docs: List[Dict[str, Any]] = []
    for path in collection_dir.glob("*.json"):
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            doc = json.loads(await f.read())
        if all(doc.get(k) == v for k, v in data.query.items()):
            docs.append(doc)

    if data.sort:
        field, _, direction = data.sort.partition(":")
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
            "data": docs[data.skip : data.skip + data.limit],
        },
    )
