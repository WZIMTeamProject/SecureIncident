import pytest
from httpx import AsyncClient
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.role import Role
from db.models.project import Project


FULL_PERMISSIONS = {
    "can_write_tickets": True,
    "can_help": True,
    "can_assign_help": True,
    "can_change_status": True,
    "can_make_roles": True,
    "can_change_roles": True,
    "can_assign_people_to_project": True,
}


class TestListRoles:

    async def test_list_roles_returns_200_when_member_requests(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_membership,
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/roles",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

    async def test_list_roles_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
        test_project: Project,
    ):
        response = await client.get(f"/api/projects/{test_project.id}/roles")
        assert response.status_code == 401

    async def test_list_roles_returns_403_when_not_member(
        self,
        client: AsyncClient,
        non_member_headers: dict,
        test_project: Project,
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/roles",
            headers=non_member_headers,
        )
        assert response.status_code == 403

    async def test_list_roles_returns_404_when_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        response = await client.get(
            f"/api/projects/{uuid4()}/roles",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestCreateRole:

    async def test_create_role_returns_201_when_owner_provides_all_permissions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=auth_headers,
            json={"name": "Reviewer", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data

    async def test_create_role_persists_role_with_correct_flags_in_db(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        db: AsyncSession,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=auth_headers,
            json={"name": "Reviewer", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 201
        data = response.json()
        result = await db.execute(select(Role).where(Role.id == UUID(data["id"])))
        role = result.scalar_one_or_none()
        assert role is not None
        assert role.can_write_tickets is True
        assert role.can_make_roles is True
        assert role.project_id == test_project.id

    async def test_create_role_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
        test_project: Project,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            json={"name": "Reviewer", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 401

    async def test_create_role_returns_403_when_not_member(
        self,
        client: AsyncClient,
        non_member_headers: dict,
        test_project: Project,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=non_member_headers,
            json={"name": "Reviewer", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 403

    async def test_create_role_returns_403_when_member_not_owner(
        self,
        client: AsyncClient,
        limited_headers: dict,
        limited_membership,
        test_project: Project,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=limited_headers,
            json={"name": "Reviewer", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 403

    async def test_create_role_returns_404_when_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        response = await client.post(
            f"/api/projects/{uuid4()}/roles",
            headers=auth_headers,
            json={"name": "Reviewer", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 404

    async def test_create_role_returns_422_when_permissions_missing(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/roles",
            headers=auth_headers,
            json={"name": "NoPerms"},
        )
        assert response.status_code == 422


class TestGetRole:

    async def test_get_role_returns_200_when_member_requests(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_role: Role,
        test_membership,
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_role.id)
        assert data["name"] == test_role.name
        assert "permissions" in data
        assert len(data["permissions"]) == len(FULL_PERMISSIONS)

    async def test_get_role_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/roles/{test_role.id}"
        )
        assert response.status_code == 401

    async def test_get_role_returns_403_when_not_member(
        self,
        client: AsyncClient,
        non_member_headers: dict,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=non_member_headers,
        )
        assert response.status_code == 403

    async def test_get_role_returns_404_when_role_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_membership,
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/roles/{uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_get_role_returns_404_when_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_role: Role,
    ):
        response = await client.get(
            f"/api/projects/{uuid4()}/roles/{test_role.id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestUpdateRole:

    async def test_update_role_returns_204_when_owner_updates_name_and_permissions(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=auth_headers,
            json={"name": "Senior", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 204

    async def test_update_role_persists_name_and_flags_in_db(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_role: Role,
        db: AsyncSession,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=auth_headers,
            json={"name": "Updated Role", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 204
        await db.refresh(test_role)
        assert test_role.name == "Updated Role"
        assert test_role.can_write_tickets is True

    async def test_update_role_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            json={"name": "Senior", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 401

    async def test_update_role_returns_403_when_not_owner(
        self,
        client: AsyncClient,
        non_member_headers: dict,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=non_member_headers,
            json={"name": "Senior", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 403

    async def test_update_role_returns_403_when_member_not_owner(
        self,
        client: AsyncClient,
        limited_headers: dict,
        limited_membership,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=limited_headers,
            json={"name": "Senior", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 403

    async def test_update_role_returns_404_when_role_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{uuid4()}",
            headers=auth_headers,
            json={"name": "Senior", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 404

    async def test_update_role_returns_404_when_project_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_role: Role,
    ):
        response = await client.patch(
            f"/api/projects/{uuid4()}/roles/{test_role.id}",
            headers=auth_headers,
            json={"name": "Senior", "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 404

    async def test_update_role_returns_422_when_name_too_long(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_role: Role,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/roles/{test_role.id}",
            headers=auth_headers,
            json={"name": "A" * 51, "permissions": FULL_PERMISSIONS},
        )
        assert response.status_code == 422
