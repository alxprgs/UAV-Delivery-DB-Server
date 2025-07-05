from pydantic import BaseModel
from fastapi import Body

class SpecializedDBRfidCardcheckScheme(BaseModel):
    reader_code: str = Body(...)
    card_id: str = Body(...)
    token: str = Body(...)