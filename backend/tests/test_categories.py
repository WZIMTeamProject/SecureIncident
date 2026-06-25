from uuid import uuid4

import pytest
from db.models.project import Project
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestCategoryValidation:
    async def test_create_category_returns_422_when_name_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
            json={"name": "", "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_category_returns_422_when_name_exceeds_50_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
            json={"name": "a" * 51, "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_category_returns_422_when_description_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
            json={"name": "Bug", "description": ""},
        )
        assert response.status_code == 422

    async def test_create_category_returns_422_when_description_exceeds_2000_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
            json={"name": "Bug", "description": "a" * 2001},
        )
        assert response.status_code == 422

    async def test_create_category_returns_422_when_description_is_missing(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
            json={"name": "Bug"},
        )
        assert response.status_code == 422


class TestCategories:
    async def test_list_categories_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_project
    ):
        r = await client.get(f"/api/projects/{test_project.id}/categories")
        assert r.status_code == 401

    async def test_list_categories_returns_403_when_not_member(
        self, client: AsyncClient, test_project, non_member_headers
    ):
        r = await client.get(
            f"/api/projects/{test_project.id}/categories",
            headers=non_member_headers,
        )
        assert r.status_code == 403

    async def test_list_categories_returns_200_empty(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        r = await client.get(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0

    async def test_create_category_returns_403_when_no_can_make_roles(
        self, client: AsyncClient, test_project, limited_headers, limited_membership
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/categories",
            json={"name": "Security", "description": "Security issues"},
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_create_category_returns_201(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/categories",
            json={"name": "Security", "description": "Security issues"},
            headers=auth_headers,
        )
        assert r.status_code == 201
        assert "id" in r.json()

    async def test_update_category_returns_404_for_nonexistent(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        r = await client.patch(
            f"/api/projects/{test_project.id}/categories/{uuid4()}",
            json={"name": "Updated"},
            headers=auth_headers,
        )
        assert r.status_code == 404

    async def test_update_category_returns_204_and_persists(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        create_r = await client.post(
            f"/api/projects/{test_project.id}/categories",
            json={"name": "OldName", "description": "desc"},
            headers=auth_headers,
        )
        cat_id = create_r.json()["id"]
        r = await client.patch(
            f"/api/projects/{test_project.id}/categories/{cat_id}",
            json={"name": "NewName"},
            headers=auth_headers,
        )
        assert r.status_code == 204
        list_r = await client.get(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
        )
        names = [c["name"] for c in list_r.json()["items"]]
        assert "NewName" in names

    async def test_delete_category_returns_204(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        create_r = await client.post(
            f"/api/projects/{test_project.id}/categories",
            json={"name": "ToDelete", "description": "delete me"},
            headers=auth_headers,
        )
        cat_id = create_r.json()["id"]
        r = await client.delete(
            f"/api/projects/{test_project.id}/categories/{cat_id}",
            headers=auth_headers,
        )
        assert r.status_code == 204
        list_r = await client.get(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
        )
        assert list_r.json()["total"] == 0
