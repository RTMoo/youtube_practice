import enum

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, String

from .db import Base


class StatusEnum(enum.Enum):
    PROCESS = "process"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoModel(Base):
    __tablename__ = "videos_metadata"

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        server_default=func.now(),
    )
    description: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    upload_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=StatusEnum.PROCESS.value,
    )
