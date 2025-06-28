import json
from pathlib import Path

import aiofiles
from fastapi import status, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Any, Dict, List

from server import app
from server.core.functions.db_functions import check_user

@app.post(
    "/db/find/{db}/{collection}",
    status_code=status.HTTP_200_OK,
    tags=["db"]
)
async def db_find(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any],
    jwt_token: str = Header(..., alias="JWT_TOKEN")
) -> JSONResponse:
    auth_ok, user = await check_user(jwt_token=jwt_token)
    if not auth_ok:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    if not user.get("access", {}).get("find", False):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": False, "message": "No find permission"}
        )

    project_root = Path(__file__).resolve().parents[3]
    db_root = project_root / "server" / "core" / "db_files"
    collection_dir = db_root / db
    collection_dir.mkdir(parents=True, exist_ok=True)
    file_path = collection_dir / f"{collection}.json"

    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            raw = await f.read()
            documents: List[Dict[str, Any]] = json.loads(raw) if raw.strip() else []
    except FileNotFoundError:
        documents = []
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Corrupted collection file"
        )

    results = [
        doc for doc in documents
        if all(doc.get(k) == v for k, v in query.items())
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": True, "data": results}
    )
