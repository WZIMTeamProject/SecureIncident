import pytest
from fastapi import status

# ---------------------------------------------------------------------
# TESTS GET /profiles/me
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_my_profile_authenticated(client, test_user, auth_headers):
    """Test fetching own profile by an authenticated user."""
    response = await client.get("/api/profiles/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["username"] == test_user.username
    assert "bio" in data
    assert "profile_picture_url" in data


@pytest.mark.asyncio
async def test_get_my_profile_unauthenticated(client):
    """Test fetching profile without an authentication token."""
    response = await client.get("/api/profiles/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------
# TESTS PATCH /profiles/me
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_my_profile_bio(client, db, test_user, auth_headers):
    """Test correct update of the bio field."""
    payload = {"bio": "Nowe bio testowe"}
    response = await client.patch(
        "/api/profiles/me", json=payload, headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Refresh the object from the database and verify the change
    await db.refresh(test_user)
    assert test_user.bio == "Nowe bio testowe"


@pytest.mark.asyncio
async def test_update_my_profile_empty_body(client, auth_headers):
    """Test sending an empty body — should not change anything or raise an error."""
    response = await client.patch("/api/profiles/me", json={}, headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_my_profile_username_conflict(client, db, auth_headers):
    """Test attempting to change username to one that is already taken."""
    # Create a second user directly in the database to simulate the conflict
    from db.models.user import User

    drugi_user = User(
        first_name="Jan",
        last_name="Kowalski",
        username="zajety_username",
        email="jan@example.com",
        password="hashed_password",
    )
    db.add(drugi_user)
    await db.commit()

    payload = {"username": "zajety_username"}
    response = await client.patch(
        "/api/profiles/me", json=payload, headers=auth_headers
    )
    assert response.status_code == status.HTTP_409_CONFLICT


# ---------------------------------------------------------------------
# TESTS GET /api/users/search
# ---------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_users_empty_query(client, auth_headers):
    """Test validation — empty query should return a 422 error."""
    response = await client.get("/api/users/search?query=", headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_search_users_authenticated(client, auth_headers):
    """Test correct search for an authenticated user."""
    response = await client.get("/api/users/search?query=test", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "users" in data
    assert isinstance(data["users"], list)


@pytest.mark.asyncio
async def test_update_my_profile_username_unique(client, db, test_user, auth_headers):
    """Test changing username to a unique value — should return 204."""
    response = await client.patch(
        "/api/profiles/me", json={"username": "nowy_unikalny"}, headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db.refresh(test_user)
    assert test_user.username == "nowy_unikalny"


@pytest.mark.asyncio
async def test_update_my_profile_unauthenticated(client):
    """Test updating profile without a token — should return 401."""
    response = await client.patch("/api/profiles/me", json={"bio": "test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_search_users_match_in_same_org(client, db, test_org, auth_headers):
    """Test search — a user from the same org should appear in the results."""
    from db.models.user import User

    same_org_user = User(
        first_name="Anna",
        last_name="Nowak",
        username="annanovak",
        email="anna@example.com",
        password="hashed",
        is_active=True,
        organization_id=test_org.id,
    )
    db.add(same_org_user)
    await db.flush()

    response = await client.get(
        "/api/users/search?query=annanovak", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    usernames = [u["username"] for u in response.json()["users"]]
    assert "annanovak" in usernames


@pytest.mark.asyncio
async def test_search_users_no_match(client, auth_headers):
    """Test search with no matching results — should return an empty list."""
    response = await client.get(
        "/api/users/search?query=zzznomatch999", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["users"] == []


@pytest.mark.asyncio
async def test_search_users_cross_org_isolation(client, db, auth_headers):
    """Test isolation — a user with no shared org or projects should not be visible."""
    from db.models.user import User

    other_user = User(
        first_name="Obcy",
        last_name="Uzytkownik",
        username="otherorguserxyz",
        email="other@differentorg.com",
        password="hashed",
        is_active=True,
        organization_id=None,
    )
    db.add(other_user)
    await db.flush()

    response = await client.get(
        "/api/users/search?query=otherorguserxyz", headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    usernames = [u["username"] for u in response.json()["users"]]
    assert "otherorguserxyz" not in usernames


@pytest.mark.asyncio
async def test_search_users_unauthenticated(client):
    """Test search without a token — should return 401."""
    response = await client.get("/api/users/search?query=test")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_search_users_null_org_isolation(client, db):
    """Test edge case: two users with no organization should not be able to see each other."""
    from core.security import create_access_token
    from db.models.user import User

    user_a = User(
        first_name="User",
        last_name="A",
        username="noorg_user_a",
        email="usera@noorg.com",
        password="hashed",
        is_active=True,
        organization_id=None,
    )
    user_b = User(
        first_name="User",
        last_name="B",
        username="noorg_user_b",
        email="userb@noorg.com",
        password="hashed",
        is_active=True,
        organization_id=None,
    )
    db.add(user_a)
    db.add(user_b)
    await db.flush()

    headers_a = {"Authorization": f"Bearer {create_access_token(user_a.id)}"}
    response = await client.get(
        "/api/users/search?query=noorg_user_b", headers=headers_a
    )
    assert response.status_code == status.HTTP_200_OK
    usernames = [u["username"] for u in response.json()["users"]]
    assert "noorg_user_b" not in usernames
