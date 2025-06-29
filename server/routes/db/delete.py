from pathlib import Path
from typing import Any, Dict

from fastapi import status, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from server import app
from server.core.functions.db_functions import check_user, _load_json
from server.core.paths import DB_DIR

@app.post("/db/delete/{db}/{collection}", status_code=status.HTTP_200_OK, tags=["db"])
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
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": False, "message": "No delete permission"})

    if not isinstance(query, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")

    collection_dir = DB_DIR / db / collection
    if not collection_dir.exists():
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "deleted": 0})

    deleted = 0
    for path in list(collection_dir.glob("*.json")):
        doc = await _load_json(path)
        if doc is None:
            continue
        if all(doc.get(k) == v for k, v in query.items()):
            path.unlink(missing_ok=True)
            deleted += 1

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": True, "deleted": deleted})