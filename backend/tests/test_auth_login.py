from datetime import UTC, datetime

from core import security
from db.models.user import User
from httpx import AsyncClient


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

    async def test_login_remember_me_false_token_expires_in_30_minutes(
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
        token = response.json()["access_token"]
        payload = security.decode_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        now = datetime.now(UTC)
        ttl_minutes = (exp - now).total_seconds() / 60
        assert 25 < ttl_minutes < 35

    async def test_login_remember_me_true_token_expires_in_7_days(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": True,
            },
        )
        token = response.json()["access_token"]
        payload = security.decode_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        now = datetime.now(UTC)
        ttl_minutes = (exp - now).total_seconds() / 60
        assert 10000 < ttl_minutes < 10100

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
