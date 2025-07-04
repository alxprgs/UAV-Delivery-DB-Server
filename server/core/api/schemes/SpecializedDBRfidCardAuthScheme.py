from pydantic import BaseModel
from fastapi import Body

class SpecializedDBRfidCardAuthScheme(BaseModel):
    guard_code: str = Body(...)
    cardid: str = Body(...)