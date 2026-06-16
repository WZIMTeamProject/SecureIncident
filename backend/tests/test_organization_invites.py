import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.organization_invite import OrganizationInvite
from db.models.user_project import UserProject
from db.models.user import User
from db.models.organization import Organization
from core import security


@pytest.fixture(scope="function")
async def org_owner_user(db: AsyncSession, test_org: Organization) -> User:
    """The org owner — separate from test_user who is just a member."""
    owner = User(
        username=f"orgowner_{uuid4().hex[:6]}",
        email=f"orgowner_{uuid4().hex[:6]}@example.com",
        first_name="Org",
        last_name="Owner",
        password=security.hash_password("TestPassword123!"),
        is_active=True,
        organization_id=test_org.id,
    )
    db.add(owner)
    await db.flush()

    test_org.org_owner_id = owner.id
    await db.flush()

    return owner


@pytest.fixture(scope="function")
def org_owner_headers(org_owner_user: User) -> dict:
    token = security.create_access_token(org_owner_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def org_invite(db: AsyncSession, test_org: Organization, org_owner_user: User):
    """Valid org-scoped invite. Returns (invite, raw_token)."""
    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)
    invite = OrganizationInvite(
        scope="ORGANIZATION",
        organization_id=test_org.id,
        project_id=None,
        created_by_id=org_owner_user.id,
        token=token_hash,
    )
    db.add(invite)
    await db.flush()
    return invite, raw_token


@pytest.fixture(scope="function")
async def expired_org_invite(db: AsyncSession, test_org: Organization, org_owner_user: User):
    """Expired org-scoped invite. Returns (invite, raw_token)."""
    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)
    invite = OrganizationInvite(
        scope="ORGANIZATION",
        organization_id=test_org.id,
        project_id=None,
        created_by_id=org_owner_user.id,
        token=token_hash,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
    )
    db.add(invite)
    await db.flush()
    return invite, raw_token


class TestOrgInviteCreation:

    async def test_create_org_invite_returns_201_when_org_owner_requests(
        self,
        client: AsyncClient,
        org_owner_headers: dict,
    ):
        response = await client.post(
            "/api/organization/invites",
            headers=org_owner_headers,
            json={},
        )
        assert response.status_code == 201

    async def test_create_org_invite_returns_403_when_non_owner_requests(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        response = await client.post(
            "/api/organization/invites",
            headers=auth_headers,
            json={},
        )
        assert response.status_code == 403

    async def test_create_org_invite_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
    ):
        response = await client.post(
            "/api/organization/invites",
            json={},
        )
        assert response.status_code == 401


class TestOrgJoin:

    async def test_join_org_returns_204_with_valid_org_invite_token(
        self,
        client: AsyncClient,
        db: AsyncSession,
        org_invite,
    ):
        invite, raw_token = org_invite
        new_user = User(
            username=f"joiner_{uuid4().hex[:6]}",
            email=f"joiner_{uuid4().hex[:6]}@example.com",
            first_name="New",
            last_name="Joiner",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(new_user)
        await db.flush()
        token = security.create_access_token(new_user.id)

        response = await client.post(
            "/api/organization/join",
            headers={"Authorization": f"Bearer {token}"},
            json={"token": raw_token},
        )
        assert response.status_code == 204

    async def test_join_org_returns_409_when_already_in_org(
        self,
        client: AsyncClient,
        auth_headers: dict,
        org_invite,
    ):
        invite, raw_token = org_invite
        response = await client.post(
            "/api/organization/join",
            headers=auth_headers,
            json={"token": raw_token},
        )
        assert response.status_code == 409

    async def test_join_org_returns_400_when_token_is_project_scoped(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_invite,
    ):
        invite, raw_token = test_invite
        new_user = User(
            username=f"joiner2_{uuid4().hex[:6]}",
            email=f"joiner2_{uuid4().hex[:6]}@example.com",
            first_name="New",
            last_name="Joiner2",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(new_user)
        await db.flush()
        token = security.create_access_token(new_user.id)

        response = await client.post(
            "/api/organization/join",
            headers={"Authorization": f"Bearer {token}"},
            json={"token": raw_token},
        )
        assert response.status_code == 400

    async def test_join_org_returns_400_when_org_invite_expired(
        self,
        client: AsyncClient,
        db: AsyncSession,
        expired_org_invite,
    ):
        invite, raw_token = expired_org_invite
        new_user = User(
            username=f"joiner3_{uuid4().hex[:6]}",
            email=f"joiner3_{uuid4().hex[:6]}@example.com",
            first_name="New",
            last_name="Joiner3",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(new_user)
        await db.flush()
        token = security.create_access_token(new_user.id)

        response = await client.post(
            "/api/organization/join",
            headers={"Authorization": f"Bearer {token}"},
            json={"token": raw_token},
        )
        assert response.status_code == 400


class TestTwoTierInvariants:

    async def test_accepting_org_invite_creates_no_user_project_rows(
        self,
        client: AsyncClient,
        db: AsyncSession,
        org_invite,
    ):
        invite, raw_token = org_invite
        new_user = User(
            username=f"invariant_{uuid4().hex[:6]}",
            email=f"invariant_{uuid4().hex[:6]}@example.com",
            first_name="Inv",
            last_name="User",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(new_user)
        await db.flush()
        token = security.create_access_token(new_user.id)

        await client.post(
            "/api/organization/join",
            headers={"Authorization": f"Bearer {token}"},
            json={"token": raw_token},
        )

        result = await db.execute(
            select(UserProject).where(UserProject.user_id == new_user.id)
        )
        rows = result.scalars().all()
        assert len(rows) == 0

    async def test_accepting_project_invite_creates_user_project_row(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_invite,
        test_project,
        test_org,
    ):
        invite, raw_token = test_invite
        member = User(
            username=f"projmember_{uuid4().hex[:6]}",
            email=f"projmember_{uuid4().hex[:6]}@example.com",
            first_name="Proj",
            last_name="Member",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=test_org.id,
        )
        db.add(member)
        await db.flush()
        member_token = security.create_access_token(member.id)

        await client.post(
            "/api/projects/join",
            headers={"Authorization": f"Bearer {member_token}"},
            json={"token": raw_token},
        )

        result = await db.execute(
            select(UserProject).where(UserProject.user_id == member.id)
        )
        rows = result.scalars().all()
        assert len(rows) >= 1

    async def test_join_project_returns_403_when_user_from_different_org(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_invite,
    ):
        invite, raw_token = test_invite

        # Create a placeholder owner for the other org (needed for NOT NULL constraint).
        placeholder_owner = User(
            username=f"placeholder_{uuid4().hex[:6]}",
            email=f"placeholder_{uuid4().hex[:6]}@example.com",
            first_name="Place",
            last_name="Holder",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(placeholder_owner)
        await db.flush()

        other_org = Organization(
            name=f"Other Org {uuid4().hex[:6]}",
            join_code=f"OTHER_{uuid4().hex[:6]}",
            org_owner_id=placeholder_owner.id,
        )
        db.add(other_org)
        await db.flush()

        other_user = User(
            username=f"crossorg_{uuid4().hex[:6]}",
            email=f"crossorg_{uuid4().hex[:6]}@example.com",
            first_name="Cross",
            last_name="OrgUser",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=other_org.id,
        )
        db.add(other_user)
        await db.flush()

        user_token = security.create_access_token(other_user.id)

        response = await client.post(
            "/api/projects/join",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"token": raw_token},
        )
        assert response.status_code == 403


class TestRevokeInvite:

    async def test_revoke_invite_returns_204_when_creator_revokes(
        self,
        client: AsyncClient,
        db: AsyncSession,
        org_invite,
        org_owner_headers: dict,
    ):
        invite, raw_token = org_invite
        response = await client.delete(
            f"/api/invites/{raw_token}",
            headers=org_owner_headers,
        )
        assert response.status_code == 204

        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.token == security.hash_token(raw_token)
            )
        )
        assert result.scalar_one_or_none() is None

    async def test_revoke_invite_returns_204_when_project_owner_revokes(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_project,
        test_role,
        test_user,
        auth_headers: dict,
    ):
        non_owner = User(
            username=f"creator_{uuid4().hex[:6]}",
            email=f"creator_{uuid4().hex[:6]}@example.com",
            first_name="Invite",
            last_name="Creator",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=test_user.organization_id,
        )
        db.add(non_owner)
        await db.flush()

        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        invite = OrganizationInvite(
            scope="PROJECT",
            project_id=test_project.id,
            organization_id=None,
            created_by_id=non_owner.id,
            token=token_hash,
            role_id=test_role.id,
        )
        db.add(invite)
        await db.flush()

        response = await client.delete(
            f"/api/invites/{raw_token}",
            headers=auth_headers,
        )
        assert response.status_code == 204

    async def test_revoke_invite_returns_403_when_unrelated_user_attempts(
        self,
        client: AsyncClient,
        db: AsyncSession,
        org_invite,
        test_org,
    ):
        invite, raw_token = org_invite

        unrelated = User(
            username=f"unrelated_{uuid4().hex[:6]}",
            email=f"unrelated_{uuid4().hex[:6]}@example.com",
            first_name="Unrelated",
            last_name="User",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
            organization_id=test_org.id,
        )
        db.add(unrelated)
        await db.flush()
        token = security.create_access_token(unrelated.id)

        response = await client.delete(
            f"/api/invites/{raw_token}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    async def test_revoke_invite_returns_404_when_token_does_not_exist(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        fake_token = security.generate_token()
        response = await client.delete(
            f"/api/invites/{fake_token}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_revoke_invite_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
        org_invite,
    ):
        invite, raw_token = org_invite
        response = await client.delete(f"/api/invites/{raw_token}")
        assert response.status_code == 401
