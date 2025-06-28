from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseSettings):
    DOMAIN: str = "uavdb.asfes.ru"
    DEV: bool = True
    ROOT_PASSWORD: str = "root"
    BACKBLAZE_APPLICATION_KEY: str = None
    BACKBLAZE_APPLICATION_KEY_ID: str = None
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()