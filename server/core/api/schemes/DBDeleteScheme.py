from pydantic import BaseModel
from typing import Any, Dict
from fastapi import Body

class DBDeleteScheme(BaseModel):
    db: str
    collection: str
    query: Dict[str, Any] = Body(
        ...,
        openapi_examples={
            "obsolete": {
                "summary": "Удалить устаревшие элементы",
                "value": {"status": "obsolete"},
            },
            "by_name": {
                "summary": "Удалить по имени",
                "value": {"name": "Battery 4S"},
            },
        },
    )