from pydantic import BaseModel
from typing import Any, Dict
from fastapi import Body

class DBUpdateScheme(BaseModel):
    db: str
    collection: str
    query: Dict[str, Any] = Body(
        ...,
        openapi_examples={
            "activate": {
                "summary": "Перевести статус из old в active",
                "value": {
                    "filter": {"status": "old"},
                    "update": {"status": "active"},
                },
            },
            "change_name": {
                "summary": "Изменить имя",
                "value": {
                    "filter": {"name": "Battery 4S"},
                    "update": {"name": "Battery 4S Pro"},
                },
            },
        },
    )