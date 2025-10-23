from fastapi import FastAPI

from src.routers import router as video_router

app = FastAPI()
app.include_router(video_router, prefix="/api/v1", tags=["upload_video"])


@app.get("/ping/upload_video_service")
async def ping():
    return "PONG"
