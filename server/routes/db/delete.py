import aiofiles
import json

from fastapi import status, Request, Depends
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.events.viewing_event import viewing_event
from server.core.api.schemes.DBDeleteScheme import DBDeleteScheme
from server.core.security import require_access


@app.post("/db/delete/{db}/{collection}", status_code=status.HTTP_200_OK, tags=["db"])
async def db_delete(
    request: Request,
    data: DBDeleteScheme,
    user: dict = Depends(require_access("delete"))
):
    await viewing_event(request)
    collection_dir = DB_DIR / data.db / data.collection
    if not collection_dir.exists():
        return JSONResponse(status_code=200, content={"status": True, "deleted": 0})

    deleted = 0
    for path in list(collection_dir.glob("*.json")):
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            doc = json.loads(await f.read())
        if all(doc.get(k) == v for k, v in data.query.items()):
            path.unlink(missing_ok=True)
            deleted += 1

    return JSONResponse(status_code=200, content={"status": True, "deleted": deleted})