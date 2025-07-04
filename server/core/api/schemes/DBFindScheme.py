from pydantic import BaseModel
from typing import Any, Dict, Optional
from fastapi import Body

class DBFindScheme(BaseModel):
    db: str
    collection: str
    query: Dict[str, Any] = Body(
        default={},
        openapi_examples={
            "by_name": {
                "summary": "Фильтр по имени",
                "value": {"name": "Battery 4S"},
            },
            "empty": {
                "summary": "Без фильтра (вернуть все документы)",
                "value": {},
            },
        })
    skip: int = 0
    limit: int = 100
    sort: Optional[str] = None