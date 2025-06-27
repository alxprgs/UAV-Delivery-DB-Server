from server import app
from fastapi import status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class DBAuthScheme(BaseModel):
    jwt_token: str

@app.post(path="/db/auth", status_code=status.HTTP_200_OK, tags=["db"])
async def dbauth(request: Request, data: DBAuthScheme) -> JSONResponse:
    pass