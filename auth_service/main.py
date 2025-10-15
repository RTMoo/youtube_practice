from fastapi import FastAPI

from src.routers import router as auth_router

app = FastAPI(
    title="Auth Service",
    description="Сервис аутентификации",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])


@app.get("/")
async def ping():
    return {"message": "PONG", "service": "auth-service"}
