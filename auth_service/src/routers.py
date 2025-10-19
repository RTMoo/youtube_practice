from datetime import timedelta

from fastapi import APIRouter, HTTPException, Response, status
from faststream.rabbit.fastapi import RabbitRouter
from sqlalchemy.exc import IntegrityError

from .dependencies import (
    AccessTokenRequiredDep,
    RefreshTokenDep,
    RefreshTokenRequiredDep,
    UserModelDep,
)
from .redis import RedisDep
from .schemas import (
    ChangePasswordSchema,
    EmailSchema,
    ResetPasswordSchema,
    SetCredentialsSchema,
    UserLoginSchema,
)
from .services import UserServiceDep
from .settings import security, settings
from .utils import generate_token, hash_password, verify_password

router = APIRouter()
rb_router = RabbitRouter(settings.FASTSTREAM_RABBITMQ_URL)


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

    key = f"verify:token:{payload.email}"
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

    await cache.set(
        name=f"verify:email:{token}",
        ex=settings.VERIFY_TOKEN_LIFETIME,
        value=payload.email,
    )
    await cache.set(
        name=f"verify:token:{payload.email}",
        ex=settings.VERIFY_TOKEN_LIFETIME,
        value=token,
    )

    await rb_router.broker.publish(
        {
            "email": payload.email,
            "link": settings.BASE_URL + f"verify?token={token}",
        },
        queue="send_verify_token",
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

    access_token = security.create_access_token(
        uid=str(user.id),
        expiry=timedelta(minutes=30),
    )
    refresh_token = security.create_refresh_token(
        uid=str(user.id),
        expiry=timedelta(days=7),
    )

    response.set_cookie(
        "access_token",
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


@rb_router.post("/resend_verification")
async def resend_verification(
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

    key = f"verify:token:{payload.email}"
    existing_ttl = await cache.ttl(key)

    if existing_ttl > 0:
        time_passed = settings.VERIFY_TOKEN_LIFETIME - existing_ttl
        remains = settings.MIN_RESEND_TOKEN_LIFETIME - time_passed

        if remains > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Токен уже отправлен. Повторно можно через {remains} секунд.",
            )
    else:
        raise HTTPException(
            status_code=404,
            detail="Токен не найден или истёк. Пройдите регистрацию заново.",
        )
    token = await cache.get(key)
    await cache.delete(f"verify:token:{payload.email}", f"verify:email:{token}")

    token = generate_token()

    await cache.set(
        name=f"verify:email:{token}",
        ex=settings.VERIFY_TOKEN_LIFETIME,
        value=payload.email,
    )
    await cache.set(
        name=f"verify:token:{payload.email}",
        ex=settings.VERIFY_TOKEN_LIFETIME,
        value=token,
    )

    await rb_router.broker.publish(
        {
            "email": payload.email,
            "link": settings.BASE_URL + f"verify?token={token}",
        },
        queue="resend_verify_token",
    )

    return {"status": "OK"}


@router.post("/verify_email")
async def verify_email(
    token: str,
    credentials: SetCredentialsSchema,
    cache: RedisDep,
    user_service: UserServiceDep,
):
    email = await cache.get(f"verify:email:{token}")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен истек либо не запрашивался",
        )

    user = await user_service.get(email=email.decode())

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if user and user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже подтверждён.",
        )

    data = credentials.model_dump()
    data["email_verified"] = True
    data["password"] = hash_password(data["password"])

    await user_service.update(email=user.email, new_data=data)

    await cache.delete(f"verify:email:{token}", f"verify:token:{email}")


@router.get("/me")
async def get_about_me(user: UserModelDep):
    return user


@router.post("/change_password")
async def change_password(
    user: UserModelDep,
    user_service: UserServiceDep,
    payload: ChangePasswordSchema,
):
    if not verify_password(payload.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный пароль, попробуйте ещё раз или сбросьте пароль",
        )

    hashed_password = hash_password(payload.new_password)
    await user_service.update(id=user.id, new_data={"password": hashed_password})

    return {"status": "OK"}


@rb_router.post("/forgot_password")
async def forgot_password(
    payload: EmailSchema,
    cache: RedisDep,
    user_service: UserServiceDep,
):
    token_exists = await cache.exists(f"reset:token:{payload.email}")

    if token_exists:
        raise HTTPException(
            status_code=429,
            detail="Токен уже отправлен ранее.",
        )

    user = await user_service.get(email=payload.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Почта не подтверждена.",
        )

    token = generate_token()

    await cache.set(
        name=f"reset:token:{user.email}",
        ex=settings.RESET_TOKEN_LIFETIME,
        value=token,
    )
    await cache.set(
        name=f"reset:email:{token}",
        ex=settings.RESET_TOKEN_LIFETIME,
        value=user.email,
    )

    await rb_router.broker.publish(
        message={
            "email": user.email,
            "link": settings.BASE_URL + f"reset?token={token}",
        },
        queue="send_reset_password_token",
    )

    return {"status": "OK"}


@router.post("/reset_password")
async def resend_password(
    token: str,
    payload: ResetPasswordSchema,
    cache: RedisDep,
    user_service: UserServiceDep,
):
    email = await cache.get(f"reset:email:{token}")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Токен истек либо не запрашивался",
        )

    user = await user_service.get(email=email.decode())

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неправильные данные",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Почта не подтверждена.",
        )

    data = {"password": hash_password(payload.new_password)}
    await user_service.update(email=user.email, new_data=data)

    await cache.delete(f"reset:email:{token}", f"reset:token:{email}")

    return {"status": "OK"}


@router.post(
    "/logout",
    dependencies=[
        RefreshTokenRequiredDep,
        AccessTokenRequiredDep,
    ],
)
async def logout(
    response: Response,
    cache: RedisDep,
    refresh_token: RefreshTokenDep,
):
    exp = int(refresh_token.exp.timestamp())

    await cache.set(
        name=f"blacklist:{refresh_token.jti}",
        value=1,
        exat=exp,
    )

    response.delete_cookie("refresh_token", httponly=True)
    response.delete_cookie("access_token", httponly=True)

    return {"status": "OK"}


@router.post(
    "/refresh",
    dependencies=[RefreshTokenRequiredDep],
)
async def refresh(
    response: Response,
    refresh_token: RefreshTokenDep,
    cache: RedisDep,
):
    print(refresh_token.jti)
    if await cache.exists(f"blacklist:{refresh_token.jti}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не действителен.",
        )

    new_access_token = security.create_access_token(
        uid=refresh_token.sub,
    )
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
    )

    return {"status": "OK"}


router.include_router(rb_router)
