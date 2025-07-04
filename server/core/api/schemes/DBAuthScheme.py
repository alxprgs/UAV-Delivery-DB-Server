from pydantic import BaseModel

class DBAuthScheme(BaseModel):
    username: str
    password: str
