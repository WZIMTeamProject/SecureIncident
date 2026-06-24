from db.models.user import User
from httpx import AsyncClient


class TestChangePassword:
    async def test_change_password_returns_204_with_valid_data(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        r = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword123!",
            },
            headers=auth_headers,
        )
        assert r.status_code == 204

    async def test_change_password_allows_login_with_new_password(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        changed = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword123!",
            },
            headers=auth_headers,
        )
        assert changed.status_code == 204

        ok = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "NewPassword123!",
                "remember_user": False,
            },
        )
        assert ok.status_code == 200

        old = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert old.status_code == 401

    async def test_change_password_returns_400_with_wrong_current_password(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        r = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!",
            },
            headers=auth_headers,
        )
        assert r.status_code == 400

    async def test_change_password_returns_400_when_new_equals_current(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        r = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123!",
                "new_password": "TestPassword123!",
            },
            headers=auth_headers,
        )
        assert r.status_code == 400

    async def test_change_password_returns_401_without_token(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123!",
                "new_password": "NewPassword123!",
            },
        )
        assert r.status_code == 401

    async def test_change_password_returns_422_when_new_password_weak(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        r = await client.post(
            "/api/auth/change-password",
            json={"current_password": "TestPassword123!", "new_password": "weak"},
            headers=auth_headers,
        )
        assert r.status_code == 422
