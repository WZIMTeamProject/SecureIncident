import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

import aiosmtplib
from core.config import settings
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Bound the SMTP exchange so a hung server can't orphan the background task.
_SMTP_TIMEOUT_SECONDS = 30.0

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"
_jinja_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


async def send_reset_email(to: str, raw_token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    minutes = settings.PASSWORD_RESET_EXPIRE_MINUTES

    try:
        html_body = _jinja_env.get_template("password_reset.html").render(
            reset_url=reset_url, minutes=minutes
        )
    except Exception:
        logger.exception("Failed to render reset email template for %s", to)
        return

    text_body = (
        f"Reset your SecureIncident password by visiting: {reset_url}\n\n"
        f"This link expires in {minutes} minutes."
    )

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = "Reset your SecureIncident password"
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            use_tls=settings.SMTP_TLS,
            timeout=_SMTP_TIMEOUT_SECONDS,
        )
    except Exception:
        logger.exception("Failed to send reset email to %s", to)
