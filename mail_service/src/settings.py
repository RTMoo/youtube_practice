from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379/0"
    VERIFY_TOKEN_LIFETIME: int = 3600
    RESET_TOKEN_LIFETIME: int = 600
    BASE_URL: str = "http://0.0.0.0:8000/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
