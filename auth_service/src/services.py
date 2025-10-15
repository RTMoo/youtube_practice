from typing import Annotated, Any, Sequence

from fastapi import Depends
from sqlalchemy import and_, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .db import SessionDep
from .models import UserModel


class UserService:
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

    async def get(
        self,
        **filters,
    ) -> UserModel | None:
        stmt = select(UserModel).where(and_(*self._build_conditions(**filters)))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        user = UserModel(
            username=username,
            password=password,
            email=email,
        )
        self.session.add(user)
        await self.session.commit()

    async def exists(
        self,
        **filters,
    ) -> bool:
        stmt = select(exists().where(and_(*self._build_conditions(**filters))))

        return bool(await self.session.scalar(stmt))

    async def update(
        self,
        new_data: dict[str, Any],
        returning: bool = False,
        **filters,
    ) -> Sequence[UserModel] | None:
        stmt = (
            update(UserModel)
            .where(and_(*self._build_conditions(**filters)))
            .values(**new_data)
        )

        if returning:
            stmt = stmt.returning(UserModel)

            result = await self.session.execute(stmt)
            updated_rows = result.scalars().all()

            await self.session.commit()

            return updated_rows

        await self.session.execute(stmt)
        await self.session.commit()

    def _build_conditions(self, **filters):
        if not filters:
            raise ValueError("Не указаны параметры фильтрации")
        conditions = []
        for field_name, value in filters.items():
            column = getattr(UserModel, field_name, None)
            if column is None:
                raise ValueError(
                    f"Поле '{field_name}' не существует в модели UserModel"
                )
            conditions.append(column == value)
        return conditions


UserServiceDep = Annotated[UserService, Depends(UserService.from_session)]
