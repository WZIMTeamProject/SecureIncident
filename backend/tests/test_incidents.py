from httpx import AsyncClient

from db.models.project import Project


class TestIncidentValidation:
    async def test_create_incident_returns_422_when_title_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "", "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_title_exceeds_200_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "a" * 201, "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_title_is_whitespace_only(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "   ", "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_description_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "valid title", "description": ""},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_description_exceeds_2000_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "valid title", "description": "a" * 2001},
        )
        assert response.status_code == 422
