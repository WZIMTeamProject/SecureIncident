import logging
from email.message import Message
from unittest.mock import AsyncMock, MagicMock, patch

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


def _mock_smtp_client() -> MagicMock:
    mock_client = MagicMock()
    mock_client.connect = AsyncMock()
    mock_client.starttls = AsyncMock()
    mock_client.login = AsyncMock()
    mock_client.send_message = AsyncMock()
    mock_client.quit = AsyncMock()
    return mock_client


class TestSendResetEmail:
    async def test_send_reset_email_includes_reset_url_in_html_part(self):
        mock_client = _mock_smtp_client()
        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_client.send_message.call_args.args[0]
        html = _get_parts(message)["text/html"]
        assert f"token={RAW_TOKEN}" in html

    async def test_send_reset_email_includes_reset_url_in_text_part(self):
        mock_client = _mock_smtp_client()
        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_client.send_message.call_args.args[0]
        text = _get_parts(message)["text/plain"]
        assert f"token={RAW_TOKEN}" in text

    async def test_send_reset_email_attaches_both_mime_parts(self):
        mock_client = _mock_smtp_client()
        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_client.send_message.call_args.args[0]
        assert message.get_content_type() == "multipart/alternative"
        parts = _get_parts(message)
        assert "text/plain" in parts
        assert "text/html" in parts

    async def test_send_reset_email_includes_expiry_minutes(self):
        mock_client = _mock_smtp_client()
        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_client.send_message.call_args.args[0]
        minutes = settings.PASSWORD_RESET_EXPIRE_MINUTES
        text = _get_parts(message)["text/plain"]
        assert f"expires in {minutes} minutes" in text

    async def test_send_reset_email_sets_branded_subject(self):
        mock_client = _mock_smtp_client()
        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        message = mock_client.send_message.call_args.args[0]
        assert message["Subject"] == "Reset your SecureIncident password"

    async def test_send_reset_email_always_performs_starttls_handshake(self):
        mock_client = _mock_smtp_client()

        with patch(
            "services.email_service.aiosmtplib.SMTP", return_value=mock_client
        ) as mock_smtp_cls:
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        mock_smtp_cls.assert_called_once()
        assert mock_smtp_cls.call_args.kwargs["start_tls"] is False
        mock_client.connect.assert_awaited_once()
        mock_client.starttls.assert_awaited_once()
        mock_client.send_message.assert_awaited_once()
        mock_client.quit.assert_awaited_once()

    async def test_send_reset_email_blocks_send_when_starttls_fails(self):
        mock_client = _mock_smtp_client()
        mock_client.starttls = AsyncMock(side_effect=Exception("boom"))

        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        mock_client.send_message.assert_not_awaited()

    async def test_send_reset_email_blocks_send_when_login_fails(self):
        mock_client = _mock_smtp_client()
        mock_client.login = AsyncMock(side_effect=Exception("bad credentials"))

        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        mock_client.send_message.assert_not_awaited()

    async def test_send_reset_email_attempts_quit_even_when_connect_fails(self):
        mock_client = _mock_smtp_client()
        mock_client.connect = AsyncMock(side_effect=Exception("connect failed"))

        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            await send_reset_email(RECIPIENT, RAW_TOKEN)

        mock_client.quit.assert_awaited_once()

    async def test_send_reset_email_swallows_send_failure_without_raising(self, caplog):
        mock_client = _mock_smtp_client()
        mock_client.send_message = AsyncMock(side_effect=ConnectionError("smtp down"))

        with patch("services.email_service.aiosmtplib.SMTP", return_value=mock_client):
            with caplog.at_level(logging.DEBUG):
                await send_reset_email(RECIPIENT, RAW_TOKEN)

        assert len(caplog.records) > 0
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={RAW_TOKEN}"
        for record in caplog.records:
            full_message = record.getMessage()
            assert RAW_TOKEN not in full_message
            assert reset_url not in full_message
