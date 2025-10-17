from secrets import token_urlsafe
from .settings import settings


def generate_token():
    return token_urlsafe(32)


def get_link(token: str, type_: str = "verify"):
    link_temp = settings.BASE_URL + "{}" + f"?{token=}"
    if type_ == "verify":
        return link_temp.format("verify")
    if type_ == "reset_password":
        return link_temp.format("reset")

    raise ValueError
