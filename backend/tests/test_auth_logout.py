from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError

from db.models.user import User
from db.models.revoked_token import RevokedToken


def test_revoked_token_model_has_no_updated_at():
    assert not hasattr(RevokedToken, "updated_at")


class TestLogout:

    async def test_logout_returns_204_with_valid_token(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 204

    async def test_logout_returns_401_without_token(self, client: AsyncClient):
        response = await client.post("/api/auth/logout")
        assert response.status_code == 401

    async def test_logout_invalidates_token(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Verifies that the token becomes unusable after logout."""
        # 1. Log out
        logout_response = await client.post("/api/auth/logout", headers=auth_headers)
        assert logout_response.status_code == 204

        # 2. Attempt to use the same token to fetch own user data
        me_response = await client.get("/api/auth/me", headers=auth_headers)
        assert me_response.status_code == 401

    async def test_logout_is_idempotent(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Verifies that reusing the same token for logout returns 401."""
        # First logout - success
        first_logout = await client.post("/api/auth/logout", headers=auth_headers)
        assert first_logout.status_code == 204

        # Second logout with the same token - must be rejected (401) because the token is already blacklisted
        second_logout = await client.post("/api/auth/logout", headers=auth_headers)
        assert second_logout.status_code == 401

    async def test_logout_blocks_protected_endpoints(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Verifies that a revoked token blocks access to protected resources globally."""
        # Logout
        await client.post("/api/auth/logout", headers=auth_headers)

        # Attempt to access a protected endpoint — must be rejected with an auth error
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 401

    async def test_logout_returns_500_when_db_raises(
        self, db, test_user: User, auth_headers: dict
    ):
        """DB failure during token revocation must surface as 500, not be silently swallowed."""
        from main import app as fastapi_app
        from api.dependencies.db import get_db

        fastapi_app.dependency_overrides[get_db] = lambda: db

        try:
            async with AsyncClient(
                transport=ASGITransport(app=fastapi_app, raise_app_exceptions=False),
                base_url="http://test",
            ) as error_client:
                with patch(
                    "db.repositories.revoked_token_repo.add_revoked_token",
                    new_callable=AsyncMock,
                    side_effect=SQLAlchemyError("DB error"),
                ):
                    response = await error_client.post("/api/auth/logout", headers=auth_headers)
            assert response.status_code == 500
        finally:
            fastapi_app.dependency_overrides.pop(get_db, None)