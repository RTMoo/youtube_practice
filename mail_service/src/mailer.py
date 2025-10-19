from email.message import EmailMessage

import aiosmtplib

from .settings import settings
from .utils import get_subject_and_body


async def send_email(
    to_email: str,
    subject: str,
    body: str,
):
    message = EmailMessage()
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = to_email
    message["Subject"] = subject

    message.add_alternative(body, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=True,
    )


async def handle_email_message(
    email: str,
    link: str,
    type_: str,
):
    subject, body = get_subject_and_body(
        type_=type_,
        link=link,
        email=email,
    )

    await send_email(
        to_email=email,
        subject=subject,
        body=body,
    )
