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