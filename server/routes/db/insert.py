import json, uuid

import aiofiles
from fastapi import status, Request, Depends
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.events.viewing_event import viewing_event
from server.core.api.schemes.DBInsertScheme import DBInsertScheme
from server.core.security import require_access

@app.post(
    "/db/base/insert/{db}/{collection}",
    status_code=status.HTTP_201_CREATED,
    tags=["db"],
)
async def db_insert(
    request: Request,
    data: DBInsertScheme,
    user: dict = Depends(require_access("insert"))
):
    await viewing_event(request)
    collection_dir = DB_DIR / data.db / data.collection
    collection_dir.mkdir(parents=True, exist_ok=True)

    while True:
        doc_id = uuid.uuid4().hex
        file_path = collection_dir / f"{doc_id}.json"
        if not file_path.exists():
            break

    doc = {"id": doc_id, **data.query}
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(doc, ensure_ascii=False, indent=4))

    return JSONResponse(status_code=201, content={"status": True, "data": doc})
