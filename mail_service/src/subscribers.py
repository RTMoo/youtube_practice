from faststream import Logger
from .broker import broker


@broker.subscriber("send_verify_token")
async def send_verify_mail_token(email: str, link: str, logger: Logger):
    logger.info(f"send_verify_token: {email=} {link=}")


@broker.subscriber("resend_verify_token")
async def resend_verify_mail_token(email: str, link: str, logger: Logger):
    logger.info(f"resend_verify_token: {email=} {link=}")


@broker.subscriber("send_reset_password_token")
async def send_reset_password_token(email: str, link: str, logger: Logger):
    logger.info(f"send_reset_password_token: {email=} {link=}")
