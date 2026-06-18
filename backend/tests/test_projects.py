from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.user import User
from db.models.project import Project
from db.models.user_project import UserProject
from core.security import hash_password, create_access_token


class TestCreateProject:

    async def test_create_project_returns_201_when_org_member_creates_org_scope(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/api/projects",
            headers=auth_headers,
            json={"name": "New Project", "scope": "ORGANIZATION"},
        )
        assert response.status_code == 201
        assert "id" in response.json()

    async def test_create_project_returns_201_when_private_user_creates_private_scope(
        self, client: AsyncClient, db: AsyncSession
    ):
        user = User(
            username="private_user_test",
            email="private@test.example",
            first_name="Private",
            last_name="User",
            password=hash_password("Password123!"),
            organization_id=None,
        )
        db.add(user)
        await db.flush()
        token = create_access_token(user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "/api/projects",
            headers=headers,
            json={"name": "Private Project", "scope": "PRIVATE"},
        )
        assert response.status_code == 201
        assert "id" in response.json()

    async def test_create_project_returns_401_when_unauthenticated(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/projects",
            json={"name": "New Project", "scope": "ORGANIZATION"},
        )
        assert response.status_code == 401

    async def test_create_project_returns_422_when_name_missing(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            "/api/projects",
            headers=auth_headers,
            json={"scope": "ORGANIZATION"},
        )
        assert response.status_code == 422


class TestListProjects:

    async def test_list_projects_returns_200_with_member_projects(
        self, client: AsyncClient, auth_headers: dict, test_project: Project, test_membership
    ):
        response = await client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

    async def test_list_projects_returns_401_when_unauthenticated(
        self, client: AsyncClient
    ):
        response = await client.get("/api/projects")
        assert response.status_code == 401


class TestGetProject:

    async def test_get_project_returns_200_when_member_requests(
        self, client: AsyncClient, auth_headers: dict, test_project: Project, test_membership
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_project.id)
        assert data["name"] == test_project.name

    async def test_get_project_returns_401_when_unauthenticated(
        self, client: AsyncClient, test_project: Project
    ):
        response = await client.get(f"/api/projects/{test_project.id}")
        assert response.status_code == 401

    async def test_get_project_returns_403_when_not_member(
        self, client: AsyncClient, non_member_headers: dict, test_project: Project
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}", headers=non_member_headers
        )
        assert response.status_code == 403

    async def test_get_project_returns_404_when_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            f"/api/projects/{uuid4()}", headers=auth_headers
        )
        assert response.status_code == 404


class TestUpdateProject:

    async def test_update_project_returns_204_when_owner_updates_name(
        self, client: AsyncClient, auth_headers: dict, test_project: Project
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 204

    async def test_update_project_persists_name_change_in_db(
        self, client: AsyncClient, auth_headers: dict, test_project: Project, db: AsyncSession
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            headers=auth_headers,
            json={"name": "Persisted Name"},
        )
        assert response.status_code == 204
        await db.refresh(test_project)
        assert test_project.name == "Persisted Name"

    async def test_update_project_returns_401_when_unauthenticated(
        self, client: AsyncClient, test_project: Project
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 401

    async def test_update_project_returns_403_when_not_owner(
        self, client: AsyncClient, test_project: Project, limited_headers: dict, limited_membership
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            headers=limited_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 403

    async def test_update_project_returns_404_when_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.patch(
            f"/api/projects/{uuid4()}",
            headers=auth_headers,
            json={"name": "Updated Name"},
        )
        assert response.status_code == 404

    async def test_update_project_returns_422_when_name_too_long(
        self, client: AsyncClient, auth_headers: dict, test_project: Project
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}",
            headers=auth_headers,
            json={"name": "A" * 101},
        )
        assert response.status_code == 422


class TestListMembers:

    async def test_list_members_returns_200_when_member_requests(
        self, client: AsyncClient, auth_headers: dict, test_project: Project, test_membership
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/members", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["members"], list)
        first = data["members"][0]
        assert "user_id" in first
        assert "username" in first
        assert "role_id" in first
        assert "role_name" in first

    async def test_list_members_returns_401_when_unauthenticated(
        self, client: AsyncClient, test_project: Project
    ):
        response = await client.get(f"/api/projects/{test_project.id}/members")
        assert response.status_code == 401

    async def test_list_members_returns_403_when_not_member(
        self, client: AsyncClient, non_member_headers: dict, test_project: Project
    ):
        response = await client.get(
            f"/api/projects/{test_project.id}/members", headers=non_member_headers
        )
        assert response.status_code == 403

    async def test_list_members_returns_404_when_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            f"/api/projects/{uuid4()}/members", headers=auth_headers
        )
        assert response.status_code == 404


class TestAddMember:

    async def test_add_member_returns_204_when_owner_adds_valid_user(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        non_member_user: User,
        test_role,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            headers=auth_headers,
            json={"user_id": str(non_member_user.id), "role_id": str(test_role.id)},
        )
        assert response.status_code == 204

    async def test_add_member_creates_user_project_row_in_db(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        non_member_user: User,
        test_role,
        db: AsyncSession,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            headers=auth_headers,
            json={"user_id": str(non_member_user.id), "role_id": str(test_role.id)},
        )
        assert response.status_code == 204
        result = await db.execute(
            select(UserProject).where(
                UserProject.user_id == non_member_user.id,
                UserProject.project_id == test_project.id,
            )
        )
        membership = result.scalar_one_or_none()
        assert membership is not None

    async def test_add_member_returns_401_when_unauthenticated(
        self, client: AsyncClient, test_project: Project, non_member_user: User, test_role
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            json={"user_id": str(non_member_user.id), "role_id": str(test_role.id)},
        )
        assert response.status_code == 401

    async def test_add_member_returns_403_when_not_owner(
        self,
        client: AsyncClient,
        test_project: Project,
        non_member_user: User,
        test_role,
        limited_headers: dict,
        limited_membership,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            headers=limited_headers,
            json={"user_id": str(non_member_user.id), "role_id": str(test_role.id)},
        )
        assert response.status_code == 403

    async def test_add_member_returns_404_when_project_not_found(
        self, client: AsyncClient, auth_headers: dict, non_member_user: User, test_role
    ):
        response = await client.post(
            f"/api/projects/{uuid4()}/members",
            headers=auth_headers,
            json={"user_id": str(non_member_user.id), "role_id": str(test_role.id)},
        )
        assert response.status_code == 404

    async def test_add_member_returns_404_when_user_not_found(
        self, client: AsyncClient, auth_headers: dict, test_project: Project, test_role
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            headers=auth_headers,
            json={"user_id": str(uuid4()), "role_id": str(test_role.id)},
        )
        assert response.status_code == 404

    async def test_add_member_returns_404_when_role_not_in_project(
        self, client: AsyncClient, auth_headers: dict, test_project: Project, non_member_user: User
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            headers=auth_headers,
            json={"user_id": str(non_member_user.id), "role_id": str(uuid4())},
        )
        assert response.status_code == 404

    async def test_add_member_returns_409_when_user_already_member(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_role_full,
        test_user: User,
        test_membership,
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/members",
            headers=auth_headers,
            json={"user_id": str(test_user.id), "role_id": str(test_role_full.id)},
        )
        assert response.status_code == 409


class TestChangeMemberRole:

    async def test_change_member_role_returns_204_when_owner_reassigns(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        limited_membership,
        test_role_full,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/members/{limited_membership.user_id}/role",
            headers=auth_headers,
            json={"role_id": str(test_role_full.id)},
        )
        assert response.status_code == 204

    async def test_change_member_role_persists_new_role_in_db(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        limited_membership,
        test_role_full,
        db: AsyncSession,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/members/{limited_membership.user_id}/role",
            headers=auth_headers,
            json={"role_id": str(test_role_full.id)},
        )
        assert response.status_code == 204
        result = await db.execute(
            select(UserProject).where(
                UserProject.user_id == limited_membership.user_id,
                UserProject.project_id == test_project.id,
            )
        )
        membership = result.scalar_one_or_none()
        assert membership is not None
        assert membership.role_id == test_role_full.id

    async def test_change_member_role_returns_401_when_unauthenticated(
        self,
        client: AsyncClient,
        test_project: Project,
        limited_membership,
        test_role_full,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/members/{limited_membership.user_id}/role",
            json={"role_id": str(test_role_full.id)},
        )
        assert response.status_code == 401

    async def test_change_member_role_returns_403_when_not_owner(
        self,
        client: AsyncClient,
        test_project: Project,
        limited_headers: dict,
        limited_membership,
        test_role_full,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/members/{limited_membership.user_id}/role",
            headers=limited_headers,
            json={"role_id": str(test_role_full.id)},
        )
        assert response.status_code == 403

    async def test_change_member_role_returns_404_when_role_not_in_project(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        limited_membership,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/members/{limited_membership.user_id}/role",
            headers=auth_headers,
            json={"role_id": str(uuid4())},
        )
        assert response.status_code == 404

    async def test_change_member_role_returns_404_when_user_not_member(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_project: Project,
        test_role_full,
    ):
        response = await client.patch(
            f"/api/projects/{test_project.id}/members/{uuid4()}/role",
            headers=auth_headers,
            json={"role_id": str(test_role_full.id)},
        )
        assert response.status_code == 404
