from datetime import UTC, datetime, timedelta
from uuid import uuid4

from core import security
from db.models.organization_invite import OrganizationInvite
from db.models.user import User
from db.models.user_project import UserProject
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestCreateInvite:
    async def test_create_invite_returns_201_when_owner_requests(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id)},
        )
        assert response.status_code == 201

    async def test_create_invite_response_contains_raw_token(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id)},
        )
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 30

    async def test_create_invite_db_record_stores_hashed_not_raw_token(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
        db: AsyncSession,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id)},
        )
        raw_token = response.json()["token"]

        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.project_id == test_project.id
            )
        )
        invite = result.scalar_one_or_none()

        assert invite is not None
        assert invite.token != raw_token
        assert len(invite.token) == 64

    async def test_create_invite_returns_401_when_unauthenticated(
        self, client: AsyncClient, test_project, test_role
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            json={"role_id": str(test_role.id)},
        )
        assert response.status_code == 401

    async def test_create_invite_returns_403_when_not_project_owner(
        self, client: AsyncClient, test_project, test_role, db: AsyncSession
    ):
        other_user = User(
            id=uuid4(),
            first_name="Other",
            last_name="User",
            username="otheruser",
            email="other@example.com",
            password=security.hash_password("TestPassword123!"),
            is_active=True,
        )
        db.add(other_user)
        await db.commit()

        token = security.create_access_token(str(other_user.id))
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers={"Authorization": f"Bearer {token}"},
            json={"role_id": str(test_role.id)},
        )
        assert response.status_code == 403

    async def test_create_invite_returns_404_when_project_not_found(
        self, client: AsyncClient, test_role, auth_headers: dict
    ):
        fake_project_id = uuid4()
        response = await client.post(
            f"/api/projects/{fake_project_id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id)},
        )
        assert response.status_code == 404

    async def test_create_invite_returns_404_when_role_not_found(
        self, client: AsyncClient, test_project, auth_headers: dict
    ):
        fake_role_id = uuid4()
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(fake_role_id)},
        )
        assert response.status_code == 404

    async def test_create_invite_with_expiry_stores_expires_at_in_db(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
        db: AsyncSession,
    ):
        expires_at = datetime.now(UTC) + timedelta(hours=2)
        await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "expires_at": expires_at.isoformat()},
        )

        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.project_id == test_project.id
            )
        )
        invite = result.scalar_one_or_none()
        assert invite.expires_at is not None

    async def test_create_invite_with_max_uses_stores_max_uses_in_db(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
        db: AsyncSession,
    ):
        await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "max_uses": 3},
        )

        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.project_id == test_project.id
            )
        )
        invite = result.scalar_one_or_none()
        assert invite.max_uses == 3

    async def test_create_invite_stores_supplied_expires_at_without_offset(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
        db: AsyncSession,
    ):
        expires_at = datetime.now(UTC) + timedelta(hours=2)
        await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "expires_at": expires_at.isoformat()},
        )

        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.project_id == test_project.id
            )
        )
        invite = result.scalar_one_or_none()
        expected = expires_at.astimezone(UTC).replace(tzinfo=None)
        assert abs((invite.expires_at - expected).total_seconds()) < 5

    async def test_create_invite_without_expires_at_applies_default(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
        db: AsyncSession,
    ):
        await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id)},
        )

        result = await db.execute(
            select(OrganizationInvite).where(
                OrganizationInvite.project_id == test_project.id
            )
        )
        invite = result.scalar_one_or_none()
        assert invite.expires_at is not None
        expected = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=60)
        assert abs((invite.expires_at - expected).total_seconds()) < 120

    async def test_create_invite_with_past_expires_at_returns_422(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
    ):
        expires_at = datetime.now(UTC) - timedelta(hours=1)
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "expires_at": expires_at.isoformat()},
        )
        assert response.status_code == 422

    async def test_create_invite_beyond_max_cap_returns_422(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
    ):
        expires_at = datetime.now(UTC) + timedelta(hours=48)
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "expires_at": expires_at.isoformat()},
        )
        assert response.status_code == 422

    async def test_create_invite_exactly_at_cap_is_accepted(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
    ):
        # 24h is the max dropdown value and equals the cap; the 5-min skew grace must let it through.
        expires_at = datetime.now(UTC) + timedelta(hours=24)
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "expires_at": expires_at.isoformat()},
        )
        assert response.status_code == 201


class TestGetInvitePreview:
    async def test_get_invite_preview_returns_200_with_valid_token(
        self, client: AsyncClient, test_invite
    ):
        invite, raw_token = test_invite
        response = await client.get(f"/api/invites/{raw_token}")
        assert response.status_code == 200

    async def test_get_invite_preview_is_valid_true_for_active_invite(
        self, client: AsyncClient, test_invite
    ):
        invite, raw_token = test_invite
        response = await client.get(f"/api/invites/{raw_token}")
        data = response.json()
        assert data["is_valid"] is True

    async def test_get_invite_preview_is_valid_false_for_expired_invite(
        self, client: AsyncClient, expired_invite
    ):
        invite, raw_token = expired_invite
        response = await client.get(f"/api/invites/{raw_token}")
        data = response.json()
        assert data["is_valid"] is False

    async def test_get_invite_preview_is_valid_false_when_max_uses_reached(
        self, client: AsyncClient, exhausted_invite
    ):
        invite, raw_token = exhausted_invite
        response = await client.get(f"/api/invites/{raw_token}")
        data = response.json()
        assert data["is_valid"] is False

    async def test_get_invite_preview_returns_project_name_in_target_name(
        self, client: AsyncClient, test_invite, test_project
    ):
        invite, raw_token = test_invite
        response = await client.get(f"/api/invites/{raw_token}")
        data = response.json()
        assert data["target_name"] == test_project.name

    async def test_get_invite_preview_returns_404_for_unknown_token(
        self, client: AsyncClient
    ):
        fake_token = security.generate_token()
        response = await client.get(f"/api/invites/{fake_token}")
        assert response.status_code == 404

    async def test_get_invite_preview_does_not_require_authentication(
        self, client: AsyncClient, test_invite
    ):
        invite, raw_token = test_invite
        response = await client.get(f"/api/invites/{raw_token}")
        assert response.status_code in [200, 404]


class TestJoinProjectByInvite:
    async def test_join_project_returns_204_with_valid_invite(
        self, client: AsyncClient, test_user: User, test_invite, auth_headers: dict
    ):
        invite, raw_token = test_invite
        response = await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": raw_token},
        )
        assert response.status_code == 204

    async def test_join_project_creates_user_project_with_correct_role(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_invite,
        auth_headers: dict,
        db: AsyncSession,
    ):
        invite, raw_token = test_invite
        await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": raw_token},
        )

        result = await db.execute(
            select(UserProject).where(
                UserProject.user_id == test_user.id,
                UserProject.project_id == test_project.id,
            )
        )
        membership = result.scalar_one_or_none()
        assert membership is not None
        assert membership.role_id == test_invite[0].role_id

    async def test_join_project_increments_use_count(
        self,
        client: AsyncClient,
        test_user: User,
        test_invite,
        auth_headers: dict,
        db: AsyncSession,
    ):
        invite, raw_token = test_invite
        await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": raw_token},
        )

        await db.refresh(invite)
        assert invite.use_count == 1

    async def test_join_project_returns_400_with_invalid_token(
        self, client: AsyncClient, auth_headers: dict
    ):
        fake_token = security.generate_token()
        response = await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": fake_token},
        )
        assert response.status_code == 400

    async def test_join_project_returns_400_with_expired_invite(
        self, client: AsyncClient, expired_invite, auth_headers: dict
    ):
        invite, raw_token = expired_invite
        response = await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": raw_token},
        )
        assert response.status_code == 400

    async def test_join_project_returns_400_when_max_uses_exhausted(
        self, client: AsyncClient, exhausted_invite, auth_headers: dict
    ):
        invite, raw_token = exhausted_invite
        response = await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": raw_token},
        )
        assert response.status_code == 400

    async def test_join_project_returns_409_when_already_member(
        self,
        client: AsyncClient,
        test_user: User,
        test_project,
        test_role,
        auth_headers: dict,
        db: AsyncSession,
    ):
        membership = UserProject(
            user_id=test_user.id,
            project_id=test_project.id,
            role_id=test_role.id,
        )
        db.add(membership)
        await db.commit()

        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        invite = OrganizationInvite(
            id=uuid4(),
            scope="PROJECT",
            project_id=test_project.id,
            organization_id=None,
            created_by_id=test_user.id,
            token=token_hash,
            role_id=test_role.id,
            expires_at=None,
            max_uses=None,
            use_count=0,
        )
        db.add(invite)
        await db.commit()

        response = await client.post(
            "/api/projects/join",
            headers=auth_headers,
            json={"token": raw_token},
        )
        assert response.status_code == 409

    async def test_join_project_returns_401_when_unauthenticated(
        self, client: AsyncClient, test_invite
    ):
        invite, raw_token = test_invite
        response = await client.post(
            "/api/projects/join",
            json={"token": raw_token},
        )
        assert response.status_code == 401
