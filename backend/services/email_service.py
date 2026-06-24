import asyncio
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


def _build_message(to: str, raw_token: str) -> MIMEMultipart:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    minutes = settings.PASSWORD_RESET_EXPIRE_MINUTES

    html_body = _jinja_env.get_template("password_reset.html").render(
        reset_url=reset_url, minutes=minutes
    )
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
    return message


async def _connect(client: aiosmtplib.SMTP) -> None:
    await client.connect()


async def _starttls(client: aiosmtplib.SMTP) -> None:
    await client.starttls()


async def _login(client: aiosmtplib.SMTP) -> None:
    await client.login(settings.SMTP_USER, settings.SMTP_PASSWORD)


async def _send(client: aiosmtplib.SMTP, message: MIMEMultipart) -> None:
    await client.send_message(message)


async def _quit(client: aiosmtplib.SMTP, to: str) -> None:
    try:
        await asyncio.wait_for(client.quit(), timeout=_SMTP_TIMEOUT_SECONDS)
    except Exception:
        logger.debug("SMTP quit failed (connection likely already closed) for %s", to)


async def send_reset_email(to: str, raw_token: str) -> None:
    try:
        message = _build_message(to, raw_token)
    except Exception:
        logger.exception("Failed to render reset email template for %s", to)
        return

    try:
        # start_tls=False here is required, not optional: aiosmtplib's connect() auto-negotiates
        # STARTTLS internally unless this is False, which would make the explicit _starttls()
        # call below raise "Connection already using TLS". Do not flip this to True.
        client = aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            timeout=_SMTP_TIMEOUT_SECONDS,
            start_tls=False,
        )
    except Exception:
        logger.exception("Failed to construct SMTP client for %s", to)
        return

    try:
        current_step = "connect"
        await _connect(client)
        current_step = "starttls"
        await _starttls(client)
        current_step = "login"
        await _login(client)
        current_step = "send"
        await _send(client, message)
    except Exception:
        if current_step == "connect":
            logger.exception("SMTP connect failed for %s", to)
        elif current_step == "starttls":
            logger.exception("SMTP STARTTLS handshake failed for %s", to)
        elif current_step == "login":
            logger.exception("SMTP login failed for %s", to)
        else:
            logger.exception("Failed to send reset email to %s", to)
        return
    finally:
        await _quit(client, to)
