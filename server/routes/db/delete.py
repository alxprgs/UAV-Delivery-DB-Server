import json
from pathlib import Path

import aiofiles
from fastapi import status, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Any, Dict, List, Tuple

from server import app
from server.core.functions.db_functions import check_user

@app.post(
    "/db/delete/{db}/{collection}",
    status_code=status.HTTP_200_OK,
    tags=["db"]
)
async def db_delete(
    request: Request,
    db: str,
    collection: str,
    query: Dict[str, Any],
    jwt_token: str = Header(..., alias="JWT_TOKEN")
) -> JSONResponse:
    auth_ok, user = await check_user(jwt_token=jwt_token)
    if not auth_ok:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    if not user.get("access", {}).get("delete", False):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"status": False, "message": "No delete permission"}
        )

    project_root = Path(__file__).resolve().parents[3]
    db_root = project_root / "server" / "core" / "db_files"
    collection_dir = db_root / db
    collection_dir.mkdir(parents=True, exist_ok=True)
    file_path = collection_dir / f"{collection}.json"

    try:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            raw = await f.read()
            docs: List[Dict[str, Any]] = json.loads(raw) if raw.strip() else []
    except FileNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": True, "deleted": 0, "message": "Collection not found, nothing deleted"}
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Corrupted collection file"
        )

    to_keep: List[Dict[str, Any]] = []
    deleted_count = 0

    for doc in docs:
        if all(doc.get(k) == v for k, v in query.items()):
            deleted_count += 1
        else:
            to_keep.append(doc)

    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(to_keep, ensure_ascii=False, indent=4))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": True,
            "deleted": deleted_count,
            "filter": query
        }
    )
