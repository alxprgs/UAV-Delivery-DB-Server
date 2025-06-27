from server import app
from fastapi import status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class DBInsertScheme(BaseModel):
    jwt_token: str

@app.post(path="/db/insert", status_code=status.HTTP_201_CREATED, tags=["db"])
async def dbinsert(request: Request, data: DBInsertScheme) -> JSONResponse:
    pass