import json
import uuid
from pathlib import Path

import aiofiles
from fastapi import status, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Dict, Any

from server import app
from server.core.functions.db_functions import check_user

@app.post(
    path="/db/insert/{db}/{collection}",
    status_code=status.HTTP_201_CREATED,
    tags=["db"]
)
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
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": False, "message": "No insert permission"}
        )

    project_root = Path(__file__).resolve().parents[3]
    db_root = project_root / "server" / "core" / "db_files"
    collection_dir = db_root / db
    collection_dir.mkdir(parents=True, exist_ok=True)
    file_path = collection_dir / f"{collection}.json"

    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            raw = await f.read()
            documents = json.loads(raw) if raw.strip() else []
    except FileNotFoundError:
        documents = []
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "message": "Corrupted collection file"}
        )

    existing_ids = {doc.get("id") for doc in documents if "id" in doc}
    new_id = None
    while True:
        candidate = uuid.uuid4().hex
        if candidate not in existing_ids:
            new_id = candidate
            break

    new_doc = {"id": new_id, **query}
    documents.append(new_doc)

    async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
        await f.write(json.dumps(documents, ensure_ascii=False, indent=4))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"status": True, "message": "Inserted", "data": new_doc}
    )
