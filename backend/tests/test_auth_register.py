from httpx import AsyncClient
from db.models.user import User
 
 
class TestRegister:
 
    async def test_register_returns_201_with_valid_data(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
 
    async def test_register_returns_409_when_username_already_exists(
        self, client: AsyncClient, test_user: User
    ):
        
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "username": test_user.username,
                "email": "jane@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 409
 
    async def test_register_returns_409_when_email_already_exists(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "username": "janedoe",
                "email": test_user.email,
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 409
 
    async def test_register_returns_422_when_password_too_short(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "abc",
            },
        )
        assert response.status_code == 422
 
    async def test_register_returns_422_when_password_no_uppercase(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepass123!",
            },
        )
        assert response.status_code == 422
 
    async def test_register_returns_422_when_password_no_digit(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass!",
            },
        )
        assert response.status_code == 422
 
    async def test_register_returns_422_when_password_over_72_chars(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "A" * 73 + "1!",
            },
        )
        assert response.status_code == 422
 
    async def test_register_returns_422_when_email_invalid(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "invalid-email",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422
 
    async def test_register_returns_422_when_username_too_short(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "ab",
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422

    async def test_register_returns_422_when_first_name_is_empty(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422

    async def test_register_returns_422_when_last_name_is_empty(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422

    async def test_register_returns_422_when_first_name_exceeds_50_chars(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "A" * 51,
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422

    async def test_register_returns_422_when_last_name_exceeds_50_chars(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "A" * 51,
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422

    async def test_register_returns_422_when_username_exceeds_50_chars(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "username": "a" * 51,
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
        )
        assert response.status_code == 422