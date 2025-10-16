from authx.exceptions import JWTDecodeError
from fastapi import FastAPI

from src.exceptions import jwt_decode_error_handler
from src.routers import router as auth_router

app = FastAPI(
    title="Auth Service",
    description="Сервис аутентификации",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.add_exception_handler(JWTDecodeError, jwt_decode_error_handler)


@app.get("/")
async def ping():
    return {"message": "PONG", "service": "auth-service"}
