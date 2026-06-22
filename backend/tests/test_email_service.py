import logging
from email.message import Message
from unittest.mock import AsyncMock, patch

from core.config import settings
from services.email_service import send_reset_email

RAW_TOKEN = "abc123rawtoken456def"
RECIPIENT = "user@example.com"


def _get_parts(message: Message) -> dict[str, str]:
    parts: dict[str, str] = {}
    for part in message.walk():
        content_type = part.get_content_type()
        if content_type in ("text/plain", "text/html"):
            parts[content_type] = part.get_payload(decode=True).decode("utf-8")
    return parts


class TestSendResetEmail:

    async def test_send_reset_email_includes_reset_url_in_html_part(self):
        with patch(
            "services.email_service.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_send.call_args.args[0]
        html = _get_parts(message)["text/html"]
        assert f"token={RAW_TOKEN}" in html

    async def test_send_reset_email_includes_reset_url_in_text_part(self):
        with patch(
            "services.email_service.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_send.call_args.args[0]
        text = _get_parts(message)["text/plain"]
        assert f"token={RAW_TOKEN}" in text

    async def test_send_reset_email_attaches_both_mime_parts(self):
        with patch(
            "services.email_service.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_send.call_args.args[0]
        assert message.get_content_type() == "multipart/alternative"
        parts = _get_parts(message)
        assert "text/plain" in parts
        assert "text/html" in parts

    async def test_send_reset_email_includes_expiry_minutes(self):
        with patch(
            "services.email_service.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_send.call_args.args[0]
        minutes = settings.PASSWORD_RESET_EXPIRE_MINUTES
        text = _get_parts(message)["text/plain"]
        assert f"expires in {minutes} minutes" in text

    async def test_send_reset_email_sets_branded_subject(self):
        with patch(
            "services.email_service.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_send.call_args.args[0]
        assert message["Subject"] == "Reset your SecureIncident password"

    async def test_send_reset_email_sets_from_display_name(self):
        with patch(
            "services.email_service.aiosmtplib.send", new_callable=AsyncMock
        ) as mock_send:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_send.call_args.args[0]
        assert "SecureIncident" in message["From"]

    async def test_send_reset_email_swallows_send_failure_without_raising(self, caplog):
        with patch(
            "services.email_service.aiosmtplib.send",
            new_callable=AsyncMock,
            side_effect=ConnectionError("smtp down"),
        ):
            with caplog.at_level(logging.DEBUG):
                await send_reset_email(RECIPIENT, RAW_TOKEN)

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={RAW_TOKEN}"
        for record in caplog.records:
            full_message = record.getMessage()
            assert RAW_TOKEN not in full_message
            assert reset_url not in full_message
