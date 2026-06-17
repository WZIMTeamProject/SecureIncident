from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.project import Project
from db.models.role import Role
from db.models.user import User
from core.security import hash_password, create_access_token


class TestBlankNameValidation:
    """Pydantic Field(min_length=1) rejects blank names before service logic."""

    async def test_create_organization_returns_422_when_name_is_empty(
        self, client: AsyncClient, db: AsyncSession
    ):
        user = User(
            username=f"noorg_{uuid4().hex[:6]}",
            email=f"noorg_{uuid4().hex[:6]}@example.com",
            first_name="No",
            last_name="Org",
            password=hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(user)
        await db.flush()
        token = create_access_token(user.id)

        response = await client.post(
            "/api/organization",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_create_project_returns_422_when_name_is_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/api/projects",
            headers=auth_headers,
            json={"name": "", "scope": "ORGANIZATION"},
        )
        assert response.status_code == 422

    async def test_create_role_returns_422_when_name_is_empty(
        self, client: AsyncClient, test_project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=auth_headers,
            json={
                "name": "",
                "permissions": {
                    "can_write_tickets": False,
                    "can_help": False,
                    "can_assign_help": False,
                    "can_change_status": False,
                    "can_make_roles": False,
                    "can_change_roles": False,
                    "can_assign_people_to_project": False,
                },
            },
        )
        assert response.status_code == 422

    async def test_create_organization_returns_422_when_name_exceeds_100_chars(
        self, client: AsyncClient, db: AsyncSession
    ):
        user = User(
            username=f"longorg_{uuid4().hex[:6]}",
            email=f"longorg_{uuid4().hex[:6]}@example.com",
            first_name="Long",
            last_name="Name",
            password=hash_password("TestPassword123!"),
            is_active=True,
            organization_id=None,
        )
        db.add(user)
        await db.flush()
        token = create_access_token(user.id)

        response = await client.post(
            "/api/organization",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "a" * 101},
        )
        assert response.status_code == 422

    async def test_create_project_returns_422_when_name_exceeds_100_chars(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/api/projects",
            headers=auth_headers,
            json={"name": "a" * 101, "scope": "ORGANIZATION"},
        )
        assert response.status_code == 422

    async def test_create_role_returns_422_when_name_exceeds_50_chars(
        self, client: AsyncClient, test_project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=auth_headers,
            json={
                "name": "a" * 51,
                "permissions": {
                    "can_write_tickets": False,
                    "can_help": False,
                    "can_assign_help": False,
                    "can_change_status": False,
                    "can_make_roles": False,
                    "can_change_roles": False,
                    "can_assign_people_to_project": False,
                },
            },
        )
        assert response.status_code == 422


class TestUpdateProjectNameValidation:
    """UpdateProjectRequest.name is optional but when provided must satisfy min_length=1, max_length=100."""

    async def test_update_project_returns_422_when_name_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            headers=auth_headers,
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_update_project_returns_422_when_name_exceeds_100_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            headers=auth_headers,
            json={"name": "a" * 101},
        )
        assert response.status_code == 422


class TestUpdateRoleNameValidation:
    """UpdateRoleRequest.name is optional but when provided must satisfy min_length=1, max_length=50."""

    async def test_update_role_returns_422_when_name_is_empty(
        self, client: AsyncClient, test_project: Project, test_role: Role, auth_headers: dict
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=auth_headers,
            json={"name": ""},
        )
        assert response.status_code == 422

    async def test_update_role_returns_422_when_name_exceeds_50_chars(
        self, client: AsyncClient, test_project: Project, test_role: Role, auth_headers: dict
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=auth_headers,
            json={"name": "a" * 51},
        )
        assert response.status_code == 422


class TestInviteValidation:
    """CreateInviteRequest.max_uses must be gt=0 when provided."""

    async def test_create_invite_returns_422_when_max_uses_is_zero(
        self, client: AsyncClient, test_project: Project, test_role: Role, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "max_uses": 0},
        )
        assert response.status_code == 422

    async def test_create_invite_returns_422_when_max_uses_is_negative(
        self, client: AsyncClient, test_project: Project, test_role: Role, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/invites",
            headers=auth_headers,
            json={"role_id": str(test_role.id), "max_uses": -1},
        )
        assert response.status_code == 422


class TestPasswordResetValidation:
    """PasswordResetRequest and PasswordResetConfirmRequest field length constraints."""

    async def test_request_password_reset_returns_422_when_email_or_username_exceeds_100_chars(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": "a" * 101},
        )
        assert response.status_code == 422

    async def test_reset_password_returns_422_when_reset_token_exceeds_255_chars(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/reset-password",
            json={"reset_token": "a" * 256, "new_password": "ValidPass123!"},
        )
        assert response.status_code == 422
