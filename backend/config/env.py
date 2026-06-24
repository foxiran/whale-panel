import os

from pydantic_settings import BaseSettings
from typing import Optional


class Setting(BaseSettings):
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    URLPATH: str = "dashboard"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    DOC: bool = False
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRES: int = 86400  # in seconds
    PANEL_ADDRESS: str = "https://127.0.0.1:8000/dashboard"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")


config = Setting()
