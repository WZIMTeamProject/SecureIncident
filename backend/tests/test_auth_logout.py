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
        """Sprawdza, czy token staje się bezużyteczny po wylogowaniu."""
        # 1. Wylogowujemy się
        logout_response = await client.post("/api/auth/logout", headers=auth_headers)
        assert logout_response.status_code == 204

        # 2. Próbujemy użyć tego samego tokenu do pobrania danych o sobie
        me_response = await client.get("/api/auth/me", headers=auth_headers)
        assert me_response.status_code == 401

    async def test_logout_is_idempotent(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Sprawdza, czy ponowne użycie tego samego tokenu do wylogowania zwraca 401."""
        # Pierwsze wylogowanie - sukces
        first_logout = await client.post("/api/auth/logout", headers=auth_headers)
        assert first_logout.status_code == 204

        # Drugie wylogowanie tym samym tokenem - powinno być odrzucone (401), bo token jest już na czarnej liście
        second_logout = await client.post("/api/auth/logout", headers=auth_headers)
        assert second_logout.status_code == 401

    async def test_logout_blocks_protected_endpoints(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Sprawdza, czy unieważniony token blokuje dostęp do chronionych zasobów globalnie."""
        # Wylogowanie
        await client.post("/api/auth/logout", headers=auth_headers)

        # Próba wejścia na chroniony endpoint podweryfikowana błędem autoryzacji
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