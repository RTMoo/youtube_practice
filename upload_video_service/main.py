from fastapi import FastAPI

app = FastAPI()


@app.get("/ping/upload_video_service")
async def ping():
    return "PONG"
