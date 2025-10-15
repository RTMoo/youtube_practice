from sqlalchemy import Boolean, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_username"),
        UniqueConstraint("email", name="uq_email"),
    )

    username: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
