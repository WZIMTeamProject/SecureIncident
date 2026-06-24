import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestIncidentLogs:
    async def test_get_logs_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_incident, test_membership
    ):
        r = await client.get(f"/api/incidents/{test_incident.id}/logs")
        assert r.status_code == 401

    async def test_get_logs_returns_200_with_created_entry(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        # Create via HTTP to get CREATED log entry (not using test_incident which bypasses service)
        create_r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Log Test", "description": "checking logs"},
            headers=auth_headers,
        )
        assert create_r.status_code == 201
        incident_id = create_r.json()["id"]

        logs_r = await client.get(
            f"/api/incidents/{incident_id}/logs", headers=auth_headers
        )
        assert logs_r.status_code == 200
        data = logs_r.json()
        assert data["total"] >= 1
        types = [item["type"] for item in data["items"]]
        assert "CREATED" in types

    async def test_get_logs_limited_member_does_not_see_helper_added(
        self,
        client: AsyncClient,
        test_project,
        auth_headers,
        test_membership,
        limited_headers,
        limited_membership,
    ):
        create_r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Log Visibility", "description": "testing log visibility"},
            headers=auth_headers,
        )
        incident_id = create_r.json()["id"]
        await client.post(
            f"/api/incidents/{incident_id}/request-reassignment",
            headers=auth_headers,
        )

        logs_r = await client.get(
            f"/api/incidents/{incident_id}/logs", headers=limited_headers
        )
        assert logs_r.status_code == 200
        types = [item["type"] for item in logs_r.json()["items"]]
        assert "HELPER_ADDED" not in types

    async def test_get_logs_admin_sees_all_types(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        create_r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Admin Log Test", "description": "admin sees all"},
            headers=auth_headers,
        )
        incident_id = create_r.json()["id"]
        await client.post(
            f"/api/incidents/{incident_id}/request-reassignment",
            headers=auth_headers,
        )

        logs_r = await client.get(
            f"/api/incidents/{incident_id}/logs", headers=auth_headers
        )
        assert logs_r.status_code == 200
        types = [item["type"] for item in logs_r.json()["items"]]
        assert "HELPER_ADDED" in types

    async def test_get_history_returns_own_logs_only(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        create_r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "History Test", "description": "for history endpoint"},
            headers=auth_headers,
        )
        assert create_r.status_code == 201

        history_r = await client.get("/api/incidents/history", headers=auth_headers)
        assert history_r.status_code == 200
        data = history_r.json()
        assert data["total"] >= 1
        types = [item["type"] for item in data["items"]]
        assert "CREATED" in types
