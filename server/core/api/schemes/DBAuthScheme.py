from pydantic import BaseModel
from fastapi import Body

class DBAuthScheme(BaseModel):
    username: str
    password: str = Body(
        ...,
        openapi_examples={
            "root": {
                "summary": "Войти под root",
                "value": {"username": "root", "password": "<ROOT_PASSWORD>"},
            },
            "user": {
                "summary": "Войти под обычным пользователем",
                "value": {"username": "user1", "password": "<USER_PASSWORD>"},
            },
        },
    ),