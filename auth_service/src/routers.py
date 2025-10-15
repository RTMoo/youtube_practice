from fastapi import APIRouter, HTTPException, Response, status
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy.exc import IntegrityError

from .redis import RedisDep
from .schemas import (
    EmailSchema,
    SetCredentialsSchema,
    UserLoginSchema,
)
from .services import UserServiceDep
from .settings import security, settings
from .utils import generate_token, hash_password, verify_password

router = APIRouter()
rb_router = RabbitRouter(settings.FASTSTREAM_RABBITMQ_URL)
verify_token_url = "http://0.0.0.0:8000/verify?token="


@rb_router.post("/pre_register")
async def pre_register(
    payload: EmailSchema,
    user_service: UserServiceDep,
    cache: RedisDep,
):
    user = await user_service.get(email=payload.email)

    if user and user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Эта почта уже подтверждена.",
        )

    key = f"token:{payload.email}"
    token_exists = await cache.exists(key)
    if token_exists > 0:
        raise HTTPException(
            status_code=429,
            detail="Токен уже отправлен ранее.",
        )
    try:
        await user_service.create(email=payload.email)
    except IntegrityError:
        pass

    token = generate_token()

    await cache.setex(
        name=f"email:{token}",
        time=settings.TOKEN_LIFETIME,
        value=payload.email,
    )

    await cache.setex(
        name=f"token:{payload.email}",
        time=settings.TOKEN_LIFETIME,
        value=token,
    )

    await rb_router.broker.publish(
        message={
            "email": payload.email,
            "message": verify_token_url + token,
        },
        queue="send_mail",
    )

    return {"status": "OK"}


@router.post("/login")
async def login(
    credentials: UserLoginSchema,
    response: Response,
    user_service: UserServiceDep,
):
    user = await user_service.get(
        username=credentials.username,
    )

    if not user or not verify_password(
        password=credentials.password,
        hashed_password=user.password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Аккаунт заблокирован",
        )

    access_token = security.create_access_token(uid=str(user.id))
    refresh_token = security.create_refresh_token(uid=str(user.id))

    response.set_cookie(
        settings.JWT_ACCESS_COOKIE_NAME,
        access_token,
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite="lax",
    )

    return {"status": "OK"}


@rb_router.post("/resend-code")
async def resend_code(
    payload: EmailSchema,
    cache: RedisDep,
    user_service: UserServiceDep,
):
    user = await user_service.get(email=payload.email)
    if user and user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Эта почта уже подтверждена.",
        )

    key = f"token:{payload.email}"
    existing_ttl = await cache.ttl(key)

    if existing_ttl > 0:
        time_passed = settings.TOKEN_LIFETIME - existing_ttl
        remains = settings.MIN_RESEND_TOKEN_LIFETIME - time_passed

        if remains > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Код уже отправлен. Повторно можно через {remains} секунд.",
            )
    else:
        raise HTTPException(
            status_code=404,
            detail="Токен не найден или истёк. Пройдите регистрацию заново.",
        )

    token = await cache.get(key)
    if not token:
        raise HTTPException(
            status_code=404,
            detail="Токен не найден или истёк. Пройдите регистрацию заново.",
        )
    token = token.decode()

    await rb_router.broker.publish(
        message={
            "email": payload.email,
            "message": verify_token_url + token,
        },
        queue="send_mail",
    )

    return {"status": "OK"}


@router.post("/set")
async def set_new_credentials(
    token: str,
    credentials: SetCredentialsSchema,
    cache: RedisDep,
    user_service: UserServiceDep,
):
    email = await cache.get(f"email:{token}")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек либо не запрашивался",
        )
    email = email.decode()

    user = await user_service.get(email=email)

    if user and user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже подтверждён.",
        )

    data = credentials.model_dump()
    data["email_verified"] = True
    data["password"] = hash_password(data["password"])

    await user_service.update(email=email, new_data=data)

    await cache.delete(f"email:{token}")
    await cache.delete(f"token:{email}")


router.include_router(rb_router)
