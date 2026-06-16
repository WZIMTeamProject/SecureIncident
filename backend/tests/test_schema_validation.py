from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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
