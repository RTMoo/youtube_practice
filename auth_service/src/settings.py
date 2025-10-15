from datetime import timedelta
from pathlib import Path

from authx import AuthX, AuthXConfig
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+aiosqlite:///{ROOT_DIR}/db.sqlite3"

    JWT_SECRET_KEY: str = "JWT_SECRET_KEY"
    JWT_ACCESS_COOKIE_NAME: str = "access_token"
    JWT_TOKEN_LOCATION: list[str] = ["cookies"]
    JWT_REFRESH_COOKIE_NAME: str = "refresh_token"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=7)

    FASTSTREAM_RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    MIN_RESEND_TOKEN_LIFETIME: int = 60
    TOKEN_LIFETIME: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


auth_config = AuthXConfig(
    JWT_SECRET_KEY=settings.JWT_SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME=settings.JWT_ACCESS_COOKIE_NAME,
    JWT_TOKEN_LOCATION=settings.JWT_TOKEN_LOCATION,
    JWT_REFRESH_COOKIE_NAME=settings.JWT_REFRESH_COOKIE_NAME,
    JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES=settings.JWT_REFRESH_TOKEN_EXPIRES,
)

security = AuthX(config=auth_config)
