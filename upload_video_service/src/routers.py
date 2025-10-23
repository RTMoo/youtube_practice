from fastapi import APIRouter

from .schemas import InitVideoSchema
from .services import VideoServiceDep
from .utils import generate_upload_path

router = APIRouter()


@router.post("/init")
async def init_video(
    payload: InitVideoSchema,
    video_service: VideoServiceDep,
):
    upload_path = generate_upload_path()
    upload_path.resolve().mkdir(exist_ok=True, parents=True)

    data = payload.model_dump() | {"upload_path": str(upload_path)}

    video = await video_service.create(data)

    return video
