from authx.exceptions import JWTDecodeError
from fastapi import Request
from fastapi.responses import JSONResponse


async def jwt_decode_error_handler(request: Request, exc: Exception):
    if isinstance(exc, JWTDecodeError):
        return JSONResponse(
            status_code=401,
            content={"detail": "JWT Токен истек или не валиден."},
        )
    # На случай, если сюда попадёт другой тип
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
