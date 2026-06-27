from datetime import UTC, datetime

from core import security
from core.config import settings
from db.models.user import User
from httpx import AsyncClient


def _refresh_cookie_max_age(response: object) -> int:
    """Extract the refresh cookie's Max-Age (seconds) from the Set-Cookie header.

    httpx's cookie jar drops Max-Age, so the raw header is parsed directly.
    """
    for header in response.headers.get_list("set-cookie"):
        if header.startswith(f"{settings.REFRESH_COOKIE_NAME}="):
            for part in header.split(";"):
                part = part.strip()
                if part.lower().startswith("max-age="):
                    return int(part.split("=", 1)[1])
    raise AssertionError("refresh_token Set-Cookie header with Max-Age not found")


def _access_token_ttl_minutes(token: str) -> float:
    payload = security.decode_token(token)
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    return (exp - datetime.now(UTC)).total_seconds() / 60


class TestLogin:
    async def test_login_returns_200_with_valid_credentials(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["token_type"] == "bearer"

    async def test_login_response_contains_access_token_and_user(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        data = response.json()
        assert data["user"]["id"] == str(test_user.id)
        assert data["user"]["username"] == test_user.username

    async def test_login_returns_401_with_wrong_password(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "WrongPassword123!",
                "remember_user": False,
            },
        )
        assert response.status_code == 401

    async def test_login_returns_401_with_nonexistent_username(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert response.status_code == 401

    async def test_login_returns_403_when_user_inactive(
        self, client: AsyncClient, inactive_user: User
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": inactive_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert response.status_code == 403

    async def test_login_same_error_for_wrong_password_and_wrong_username(
        self, client: AsyncClient, test_user: User
    ):
        response_wrong_pw = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "WrongPassword123!",
                "remember_user": False,
            },
        )
        response_wrong_user = await client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert response_wrong_pw.status_code == response_wrong_user.status_code == 401
        assert (
            response_wrong_pw.json()["detail"] == response_wrong_user.json()["detail"]
        )

    async def test_login_remember_me_false_access_ttl_15_min_refresh_cookie_1_day(
        self, client: AsyncClient, test_user: User
    ):
        """remember_user=False: flat 15-min access TTL; refresh cookie ~1 day."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )

        # Access token TTL is a FLAT 15 min regardless of remember_user.
        ttl_minutes = _access_token_ttl_minutes(response.json()["access_token"])
        assert 14 < ttl_minutes < 16

        # remember_user drives the REFRESH cookie lifetime, not the access token.
        assert (
            _refresh_cookie_max_age(response)
            == settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )

    async def test_login_remember_me_true_access_ttl_15_min_refresh_cookie_30_days(
        self, client: AsyncClient, test_user: User
    ):
        """remember_user=True: access TTL still 15 min; refresh cookie ~30 days."""
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": True,
            },
        )

        # Access TTL is unchanged by remember_user — still a flat 15 min.
        ttl_minutes = _access_token_ttl_minutes(response.json()["access_token"])
        assert 14 < ttl_minutes < 16

        # remember_user extends ONLY the refresh cookie Max-Age (~30 days).
        assert (
            _refresh_cookie_max_age(response)
            == settings.REFRESH_TOKEN_REMEMBER_EXPIRE_MINUTES * 60
        )

    async def test_login_returns_422_when_username_exceeds_50_chars(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "a" * 51,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert response.status_code == 422

    async def test_login_returns_422_when_password_exceeds_72_chars(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": "johndoe",
                "password": "A" * 73,
                "remember_user": False,
            },
        )
        assert response.status_code == 422
