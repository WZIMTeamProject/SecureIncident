from unittest.mock import AsyncMock, patch

from core import security
from core.config import settings
from db.models.revoked_token import RevokedToken
from db.models.user import User
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError


def _refresh_cookie_value(response: object) -> str:
    """Extract the raw refresh-token value from the Set-Cookie header."""
    for header in response.headers.get_list("set-cookie"):
        if header.startswith(f"{settings.REFRESH_COOKIE_NAME}="):
            return header.split(";", 1)[0].split("=", 1)[1]
    raise AssertionError("refresh_token Set-Cookie header not found")


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

    async def test_logout_revokes_same_family_access_token(
        self, client: AsyncClient, test_user: User
    ):
        """A still-valid SAME-FAMILY access token is rejected after logout.

        Logout revokes the whole refresh family, so a fresh token minted in that
        family (different jti — bypasses the jti denylist) is caught by the new
        family check, not the jti check.
        """
        login = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        original_token = login.json()["access_token"]
        family_id = security.decode_token(original_token)["family_id"]

        # Mint a fresh, still-unexpired token in the SAME family (new jti).
        same_family_token = security.create_access_token(test_user.id, family_id)

        logout = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {original_token}"},
        )
        assert logout.status_code == 204

        me = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {same_family_token}"},
        )
        assert me.status_code == 401
        assert me.json()["detail"] == "Token has been revoked"

    async def test_me_rejects_access_token_from_reuse_revoked_family(
        self, client: AsyncClient, test_user: User
    ):
        """Reuse detection revokes the family; its access tokens are then rejected.

        Replaying a consumed refresh token trips reuse detection and denylists the
        family. A fresh access token minted in that family must fail at /me.
        """
        login = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        family_id = security.decode_token(login.json()["access_token"])["family_id"]
        first_refresh_cookie = _refresh_cookie_value(login)

        # Consume the original refresh token once (rotates to a new one).
        client.cookies.clear()
        client.cookies.set(settings.REFRESH_COOKIE_NAME, first_refresh_cookie)
        first = await client.post("/api/auth/refresh")
        assert first.status_code == 200

        # Replay the now-consumed token -> reuse detected -> family revoked.
        client.cookies.clear()
        client.cookies.set(settings.REFRESH_COOKIE_NAME, first_refresh_cookie)
        replay = await client.post("/api/auth/refresh")
        assert replay.status_code == 401

        # A fresh access token in the revoked family is rejected by /me.
        revoked_family_token = security.create_access_token(test_user.id, family_id)
        me = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {revoked_family_token}"},
        )
        assert me.status_code == 401
        assert me.json()["detail"] == "Token has been revoked"

    async def test_logout_returns_500_when_db_raises(
        self, db, test_user: User, auth_headers: dict
    ):
        """DB failure during token revocation must surface as 500, not be silently swallowed."""
        from api.dependencies.db import get_db
        from main import app as fastapi_app

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
                    response = await error_client.post(
                        "/api/auth/logout", headers=auth_headers
                    )
            assert response.status_code == 500
        finally:
            fastapi_app.dependency_overrides.pop(get_db, None)
