import json

import aiofiles
from fastapi import status, Request, Depends
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.events.viewing_event import viewing_event
from server.core.api.schemes.DBUpdateScheme import DBUpdateScheme
from server.core.security import require_access

@app.post(
    "/db/base/update/{db}/{collection}",
    status_code=status.HTTP_200_OK,
    tags=["db"],
)
async def db_update(
    request: Request,
    data: DBUpdateScheme,
    user: dict = Depends(require_access("update"))
):
    await viewing_event(request)
    filter_ = data.query.get("filter")
    update_data = data.query.get("update")
    if not isinstance(filter_, dict) or not isinstance(update_data, dict):
        return JSONResponse(
            status_code=400,
            content={"status": False, "message": "Body должен содержать 'filter' и 'update'"},
        )

    collection_dir = DB_DIR / data.db / data.collection
    if not collection_dir.exists():
        return JSONResponse(status_code=200, content={"status": True, "updated": 0})

    updated = 0
    for path in collection_dir.glob("*.json"):
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            doc = json.loads(await f.read())
        if all(doc.get(k) == v for k, v in filter_.items()):
            doc.update(update_data)
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(doc, ensure_ascii=False, indent=4))
            updated += 1

    return JSONResponse(status_code=200, content={"status": True, "updated": updated})
