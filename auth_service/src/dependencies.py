from typing import Annotated

from authx import TokenPayload
from fastapi import Depends

from .services import UserModel, UserServiceDep
from .settings import security

TokenDep = Annotated[TokenPayload, Depends(security.access_token_required)]


async def get_user(
    token: TokenDep,
    user_service: UserServiceDep,
):
    user = await user_service.get(id=token.sub)

    return user


UserModelDep = Annotated[UserModel, Depends(get_user)]
