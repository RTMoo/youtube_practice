from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis


async def get_redis() -> Redis:
    return Redis.from_url("redis://redis:6379/0")


RedisDep = Annotated[Redis, Depends(get_redis)]
