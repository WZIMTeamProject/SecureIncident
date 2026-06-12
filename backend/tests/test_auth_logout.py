import pytest
from httpx import AsyncClient

from db.models.user import User


class TestLogout:

    async def test_logout_returns_204_with_valid_token(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 204

    async def test_logout_returns_401_without_token(self, client: AsyncClient):
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401