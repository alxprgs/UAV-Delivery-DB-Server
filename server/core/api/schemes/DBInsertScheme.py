from pydantic import BaseModel
from typing import Any, Dict
from fastapi import Body

class DBInsertScheme(BaseModel):
    db: str
    collection: str
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
    )