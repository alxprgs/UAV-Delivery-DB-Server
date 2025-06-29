from typing import Any, Dict
import aiofiles
import json

from fastapi import status, Body, Depends
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.core.security import require_access


@app.post("/db/delete/{db}/{collection}", status_code=status.HTTP_200_OK, tags=["db"])
async def db_delete(
    db: str,
    collection: str,
    query: Dict[str, Any] = Body(
        ...,
        examples={
            "obsolete": {
                "summary": "Удалить устаревшие элементы",
                "value": {"status": "obsolete"},
            },
            "by_name": {
                "summary": "Удалить по имени",
                "value": {"name": "Battery 4S"},
            },
        },
    ),
    user: Dict = Depends(require_access("delete")),
):
    collection_dir = DB_DIR / db / collection
    if not collection_dir.exists():
        return JSONResponse(status_code=200, content={"status": True, "deleted": 0})

    deleted = 0
    for path in list(collection_dir.glob("*.json")):
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            doc = json.loads(await f.read())
        if all(doc.get(k) == v for k, v in query.items()):
            path.unlink(missing_ok=True)
            deleted += 1

    return JSONResponse(status_code=200, content={"status": True, "deleted": deleted})