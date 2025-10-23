from datetime import datetime

from pydantic import BaseModel

from .models import StatusEnum


class InitVideoSchema(BaseModel):
    title: str
    description: str


class VideoSchema(InitVideoSchema):
    id: int
    upload_path: int
    created_at: datetime
    status: StatusEnum
