import pytest
from fastapi import status

# ---------------------------------------------------------------------
# TESTY GET /profiles/me
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_my_profile_authenticated(client, test_user, auth_headers):
    """Test pobierania własnego profilu przez zalogowanego użytkownika."""
    response = await client.get("/api/profiles/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.username
    assert "bio" in data
    assert "profile_picture_url" in data

@pytest.mark.asyncio
async def test_get_my_profile_unauthenticated(client):
    """Test pobierania profilu bez tokenu uwierzytelniającego."""
    response = await client.get("/api/profiles/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------
# TESTY PATCH /profiles/me
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_my_profile_bio(client, db, test_user, auth_headers):
    """Test poprawnej aktualizacji pola bio."""
    payload = {"bio": "Nowe bio testowe"}
    response = await client.patch("/api/profiles/me", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Odświeżamy obiekt z bazy i sprawdzamy zmianę
    await db.refresh(test_user)
    assert test_user.bio == "Nowe bio testowe"

@pytest.mark.asyncio
async def test_update_my_profile_empty_body(client, auth_headers):
    """Test wysłania pustego body - nie powinno nic zmienić ani rzucić błędem."""
    response = await client.patch("/api/profiles/me", json={}, headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_update_my_profile_username_conflict(client, db, auth_headers):
    """Test próby zmiany username na taki, który jest już zajęty."""
    # Tworzymy w bazie drugiego użytkownika bezpośrednio, aby zasymulować konflikt
    from db.models.user import User
    drugi_user = User(
        first_name="Jan",
        last_name="Kowalski",
        username="zajety_username",
        email="jan@example.com",
        password="hashed_password"
    )
    db.add(drugi_user)
    await db.commit()

    payload = {"username": "zajety_username"}
    response = await client.patch("/api/profiles/me", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_409_CONFLICT


# ---------------------------------------------------------------------
# TESTY GET /api/users/search
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_search_users_empty_query(client, auth_headers):
    """Test walidacji - puste zapytanie powinno zwrócić błąd 422."""
    response = await client.get("/api/users/search?query=", headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_search_users_authenticated(client, auth_headers):
    """Test poprawnego wyszukiwania dla zalogowanego użytkownika."""
    response = await client.get("/api/users/search?query=test", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)