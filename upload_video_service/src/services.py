from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import SessionDep
from .models import VideoModel


class VideoService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    @classmethod
    def from_session(
        cls,
        session: SessionDep,
    ):
        return cls(session)

    async def create(
        self,
        data: dict[str, Any],
    ):
        video = VideoModel(**data)
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)

        return video


VideoServiceDep = Annotated[VideoService, Depends(VideoService.from_session)]
