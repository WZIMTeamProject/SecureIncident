from core import security
from db.models.user import User
from httpx import AsyncClient


class TestGetMe:
    async def test_get_me_returns_200_with_valid_token(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200

    async def test_get_me_returns_correct_user_data(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.get("/api/auth/me", headers=auth_headers)
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["username"] == test_user.username

    async def test_get_me_returns_401_without_token(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    async def test_get_me_returns_401_with_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    async def test_get_me_returns_401_with_expired_token(
        self, client: AsyncClient, test_user: User
    ):
        expired_token = security.create_access_token(
            str(test_user.id), remember_user=False
        )
        payload = security.decode_token(expired_token)
        payload["exp"] = payload["exp"] - 3600
        import jwt
        from core.config import settings

        expired_token_str = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token_str}"},
        )
        assert response.status_code == 401
