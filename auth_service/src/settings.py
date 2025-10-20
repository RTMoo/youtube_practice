from datetime import timedelta
from pathlib import Path

from authx import AuthX, AuthXConfig
from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+aiosqlite:///{ROOT_DIR}/db.sqlite3"
    BASE_URL: str = "http://0.0.0.0:8000/"

    JWT_ACCESS_COOKIE_NAME: str = "access_token"
    JWT_TOKEN_LOCATION: list[str] = ["cookies", "headers"]
    JWT_REFRESH_COOKIE_NAME: str = "refresh_token"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=7)
    JWT_ALGORITHM: str
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str

    FASTSTREAM_RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    MIN_RESEND_TOKEN_LIFETIME: int = 60
    VERIFY_TOKEN_LIFETIME: int = 3600
    RESET_TOKEN_LIFETIME: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore


auth_config = AuthXConfig(
    JWT_ACCESS_COOKIE_NAME=settings.JWT_ACCESS_COOKIE_NAME,
    JWT_TOKEN_LOCATION=settings.JWT_TOKEN_LOCATION,
    JWT_REFRESH_COOKIE_NAME=settings.JWT_REFRESH_COOKIE_NAME,
    JWT_ACCESS_TOKEN_EXPIRES=settings.JWT_ACCESS_TOKEN_EXPIRES,
    JWT_REFRESH_TOKEN_EXPIRES=settings.JWT_REFRESH_TOKEN_EXPIRES,
    JWT_CSRF_METHODS=[],  # ["POST", "PUT", "PATCH", "DELETE"]
    JWT_ALGORITHM=settings.JWT_ALGORITHM,
    JWT_PRIVATE_KEY=open(settings.JWT_PRIVATE_KEY_PATH).read(),
    JWT_PUBLIC_KEY=open(settings.JWT_PUBLIC_KEY_PATH).read(),
)

security = AuthX(config=auth_config)
