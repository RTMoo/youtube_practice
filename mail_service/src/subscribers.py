from faststream import Logger
from .broker import broker
from .redis import redis as cache
from .utils import generate_token, get_link
from .settings import settings


@broker.subscriber("send_verify_token")
async def send_verify_mail_token(email: str, logger: Logger):
    token = generate_token()

    await cache.setex(f"verify:email:{token}", settings.VERIFY_TOKEN_LIFETIME, email)
    await cache.setex(f"verify:token:{email}", settings.VERIFY_TOKEN_LIFETIME, token)

    link = get_link(token, "verify")

    logger.info(f"send_verify_token: {email=} {link=}")


@broker.subscriber("resend_verify_token")
async def resend_verify_mail_token(email: str, logger: Logger):
    token = generate_token()

    await cache.setex(f"verify:email:{token}", settings.VERIFY_TOKEN_LIFETIME, email)
    await cache.setex(f"verify:token:{email}", settings.VERIFY_TOKEN_LIFETIME, token)

    link = get_link(token, "verify")

    logger.info(f"resend_verify_token: {email=} {link=}")


@broker.subscriber("send_reset_password_token")
async def send_reset_password_token(email: str, logger: Logger):
    token = generate_token()
    await cache.setex(f"reset:token:{email}", settings.RESET_TOKEN_LIFETIME, token)
    await cache.setex(f"reset:email:{token}", settings.RESET_TOKEN_LIFETIME, email)

    link = get_link(token, "reset_password")

    logger.info(f"send_reset_password_token: {email=} {link=}")
