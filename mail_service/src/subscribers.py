from faststream import Logger

from .broker import broker
from .mailer import handle_email_message


@broker.subscriber("send_verify_token")
async def send_verify_mail_token(
    email: str,
    link: str,
    logger: Logger,
):
    logger.info(f"send_verify_token: {email=} {link=}")

    await handle_email_message(
        email=email,
        link=link,
        type_="verify",
    )


@broker.subscriber("resend_verify_token")
async def resend_verify_mail_token(email: str, link: str, logger: Logger):
    logger.info(f"resend_verify_token: {email=} {link=}")

    await handle_email_message(
        email=email,
        link=link,
        type_="verify",
    )


@broker.subscriber("send_reset_password_token")
async def send_reset_password_token(email: str, link: str, logger: Logger):
    logger.info(f"send_reset_password_token: {email=} {link=}")

    await handle_email_message(
        email=email,
        link=link,
        type_="reset",
    )
