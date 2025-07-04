import json, uuid
from pathlib import Path
from typing import Dict, Any

import aiofiles
from fastapi import status, Request, Depends, Body
from fastapi.responses import JSONResponse

from server import app
from server.core.paths import DB_DIR
from server.core.security import require_access
from server.events.viewing_event import viewing_event

@app.post(
    "/db/insert/{db}/{collection}",
    status_code=status.HTTP_201_CREATED,
    tags=["db"],
)
async def db_insert(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any] = Body(
        ...,
        openapi_examples={
            "battery": {
                "summary": "Добавить аккумулятор",
                "value": {"name": "Battery 4S", "capacity": 2200, "unit": "mAh"},
            },
            "motor": {
                "summary": "Добавить мотор",
                "value": {"name": "Motor 2212", "kv": 920},
            },
        },
    ),
    user: Dict = Depends(require_access("insert")),
):
    await viewing_event(request)
    collection_dir = DB_DIR / db / collection
    collection_dir.mkdir(parents=True, exist_ok=True)

    while True:
        doc_id = uuid.uuid4().hex
        file_path = collection_dir / f"{doc_id}.json"
        if not file_path.exists():
            break

    doc = {"id": doc_id, **query}
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(doc, ensure_ascii=False, indent=4))

    return JSONResponse(status_code=201, content={"status": True, "data": doc})
