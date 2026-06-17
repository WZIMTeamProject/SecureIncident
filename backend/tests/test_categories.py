from httpx import AsyncClient

from db.models.project import Project


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
