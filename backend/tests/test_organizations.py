import uuid

from db.models.organization import Organization
from db.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestCreateOrganization:
    async def test_create_organization_returns_201_with_id(
        self, client: AsyncClient, fresh_user_headers: dict
    ):
        r = await client.post(
            "/api/organization",
            json={"name": "Acme Corp", "description": "Test org"},
            headers=fresh_user_headers,
        )
        assert r.status_code == 201
        assert "id" in r.json()

    async def test_create_organization_persists_org_row_in_db(
        self,
        client: AsyncClient,
        fresh_user_headers: dict,
        fresh_user: User,
        db: AsyncSession,
    ):
        r = await client.post(
            "/api/organization",
            json={"name": "Acme Corp", "description": "Test org"},
            headers=fresh_user_headers,
        )
        assert r.status_code == 201
        org_id = uuid.UUID(r.json()["id"])
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        org = result.scalar_one_or_none()
        assert org is not None
        assert org.name == "Acme Corp"
        assert org.org_owner_id == fresh_user.id

    async def test_create_organization_sets_creator_organization_id(
        self,
        client: AsyncClient,
        fresh_user_headers: dict,
        fresh_user: User,
        db: AsyncSession,
    ):
        r = await client.post(
            "/api/organization",
            json={"name": "Acme Corp", "description": "Test org"},
            headers=fresh_user_headers,
        )
        assert r.status_code == 201
        org_id = uuid.UUID(r.json()["id"])
        await db.refresh(fresh_user)
        assert fresh_user.organization_id == org_id

    async def test_create_organization_returns_409_when_user_already_has_org(
        self, client: AsyncClient, auth_headers: dict
    ):
        r = await client.post(
            "/api/organization",
            json={"name": "Dupe Org"},
            headers=auth_headers,
        )
        assert r.status_code == 409

    async def test_create_organization_returns_401_when_unauthenticated(
        self, client: AsyncClient
    ):
        r = await client.post(
            "/api/organization",
            json={"name": "No Auth Org"},
        )
        assert r.status_code == 401

    async def test_create_organization_returns_422_when_name_missing(
        self, client: AsyncClient, fresh_user_headers: dict
    ):
        r = await client.post(
            "/api/organization",
            json={},
            headers=fresh_user_headers,
        )
        assert r.status_code == 422

    async def test_create_organization_returns_422_when_name_exceeds_100_chars(
        self, client: AsyncClient, fresh_user_headers: dict
    ):
        r = await client.post(
            "/api/organization",
            json={"name": "A" * 101},
            headers=fresh_user_headers,
        )
        assert r.status_code == 422


class TestGetOrganization:
    async def test_get_organization_returns_200_with_correct_fields(
        self, client: AsyncClient, auth_headers: dict, test_org
    ):
        r = await client.get("/api/organization", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(test_org.id)
        assert data["name"] == test_org.name
        assert "description" in data

    async def test_get_organization_returns_404_when_user_has_no_org(
        self, client: AsyncClient, fresh_user_headers: dict
    ):
        r = await client.get("/api/organization", headers=fresh_user_headers)
        assert r.status_code == 404

    async def test_get_organization_returns_401_when_unauthenticated(
        self, client: AsyncClient
    ):
        r = await client.get("/api/organization")
        assert r.status_code == 401


class TestDeleteOrganization:
    async def test_delete_organization_returns_204_when_owner(
        self, client: AsyncClient, fresh_user_headers: dict
    ):
        created = await client.post(
            "/api/organization",
            json={"name": "Deletable Org"},
            headers=fresh_user_headers,
        )
        assert created.status_code == 201
        r = await client.delete("/api/organization", headers=fresh_user_headers)
        assert r.status_code == 204

    async def test_delete_organization_removes_org_row(
        self, client: AsyncClient, fresh_user_headers: dict, db: AsyncSession
    ):
        created = await client.post(
            "/api/organization",
            json={"name": "Deletable Org"},
            headers=fresh_user_headers,
        )
        org_id = uuid.UUID(created.json()["id"])
        r = await client.delete("/api/organization", headers=fresh_user_headers)
        assert r.status_code == 204
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        assert result.scalar_one_or_none() is None

    async def test_delete_organization_detaches_owner(
        self,
        client: AsyncClient,
        fresh_user: User,
        fresh_user_headers: dict,
        db: AsyncSession,
    ):
        await client.post(
            "/api/organization",
            json={"name": "Deletable Org"},
            headers=fresh_user_headers,
        )
        await client.delete("/api/organization", headers=fresh_user_headers)
        await db.refresh(fresh_user)
        assert fresh_user.organization_id is None

    async def test_delete_organization_returns_403_when_not_owner(
        self, client: AsyncClient, auth_headers: dict, test_org
    ):
        # test_user is a member of test_org but NOT its owner.
        r = await client.delete("/api/organization", headers=auth_headers)
        assert r.status_code == 403

    async def test_delete_organization_returns_404_when_user_has_no_org(
        self, client: AsyncClient, fresh_user_headers: dict
    ):
        r = await client.delete("/api/organization", headers=fresh_user_headers)
        assert r.status_code == 404

    async def test_delete_organization_returns_401_when_unauthenticated(
        self, client: AsyncClient
    ):
        r = await client.delete("/api/organization")
        assert r.status_code == 401
