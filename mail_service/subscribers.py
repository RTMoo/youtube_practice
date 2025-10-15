from faststream import Logger
from broker import broker


@broker.subscriber("send_mail")
async def send_mail(email: str, message: str, logger: Logger):
    logger.info(f"📩 Получено сообщение: {email} {message}")
