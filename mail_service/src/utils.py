from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

templates = {
    "verify": {
        "subject": "Подтверждение почты",
        "path": "verify_email.html",
    },
    "reset": {
        "subject": "Сброс пароля",
        "path": "reset_password.html",
    },
}


def get_subject_and_body(
    type_: str,
    link: str,
    email: str,
) -> tuple[str, str]:
    subject = templates[type_]["subject"]
    body = env.get_template(templates[type_]["path"]).render(
        link=link,
        email=email,
    )

    return subject, body
