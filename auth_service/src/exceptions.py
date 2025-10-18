from authx.exceptions import JWTDecodeError, MissingTokenError
from fastapi import Request
from fastapi.responses import JSONResponse


async def jwt_decode_error_handler(request: Request, exc: Exception):
    if isinstance(exc, JWTDecodeError):
        return JSONResponse(
            status_code=401,
            content={"detail": "Токен не валиден."},
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


async def missing_token_error_handler(request: Request, exc: Exception):
    if isinstance(exc, MissingTokenError):
        return JSONResponse(
            status_code=401,
            content={"detail": "Токена нет, заново войдите в систему"},
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
