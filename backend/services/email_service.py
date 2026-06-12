import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from core.config import settings

logger = logging.getLogger(__name__)


async def send_reset_email(to: str, raw_token: str) -> None:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = "Password Reset Request"

    text_part = MIMEText(
        f"Reset your password by visiting: {reset_url}", "plain"
    )
    html_part = MIMEText(
        f'<p>Reset your password: <a href="{reset_url}">{reset_url}</a></p>', "html"
    )
    message.attach(text_part)
    message.attach(html_part)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            use_tls=settings.SMTP_TLS,
        )
    except Exception:
        logger.exception("Failed to send reset email to %s", to)
