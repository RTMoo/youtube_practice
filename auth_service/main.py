from authx.exceptions import JWTDecodeError, MissingTokenError
from fastapi import FastAPI

from src import exceptions
from src.routers import router as auth_router

app = FastAPI(
    title="Auth Service",
    description="Сервис аутентификации",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.add_exception_handler(JWTDecodeError, exceptions.jwt_decode_error_handler)
app.add_exception_handler(MissingTokenError, exceptions.missing_token_error_handler)


@app.get("/")
async def ping():
    return {"message": "PONG", "service": "auth-service"}
