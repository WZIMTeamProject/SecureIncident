import pytest
from uuid import uuid4
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestHelpers:
    async def test_request_reassignment_returns_403_when_no_can_help(
        self, client: AsyncClient, test_incident, test_membership, limited_headers, limited_membership
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/request-reassignment",
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_request_reassignment_returns_204_and_adds_helper(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        incident_id = str(test_incident.id)
        r = await client.post(
            f"/api/incidents/{incident_id}/request-reassignment",
            headers=auth_headers,
        )
        assert r.status_code == 204
        detail = await client.get(f"/api/incidents/{incident_id}", headers=auth_headers)
        assert detail.status_code == 200
        helpers = detail.json()["helpers"]
        assert len(helpers) == 1

    async def test_request_reassignment_returns_409_when_already_helper(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        await client.post(
            f"/api/incidents/{test_incident.id}/request-reassignment",
            headers=auth_headers,
        )
        r = await client.post(
            f"/api/incidents/{test_incident.id}/request-reassignment",
            headers=auth_headers,
        )
        assert r.status_code == 409

    async def test_add_helper_returns_409_when_duplicate(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        body = {"user_id": str(test_incident.reporter_id)}
        await client.post(
            f"/api/incidents/{test_incident.id}/helpers",
            json=body,
            headers=auth_headers,
        )
        r = await client.post(
            f"/api/incidents/{test_incident.id}/helpers",
            json=body,
            headers=auth_headers,
        )
        assert r.status_code == 409

    async def test_add_helper_returns_403_when_no_can_assign_help(
        self, client: AsyncClient, test_incident, test_membership, limited_headers, limited_membership, test_user
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/helpers",
            json={"user_id": str(test_user.id)},
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_remove_helper_returns_404_when_not_a_helper(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        from uuid import uuid4
        non_helper_id = str(uuid4())
        r = await client.delete(
            f"/api/incidents/{test_incident.id}/helpers/{non_helper_id}",
            headers=auth_headers,
        )
        assert r.status_code == 404

    async def test_remove_helper_returns_204(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        await client.post(
            f"/api/incidents/{test_incident.id}/request-reassignment",
            headers=auth_headers,
        )
        helper_user_id = str(test_incident.reporter_id)
        r = await client.delete(
            f"/api/incidents/{test_incident.id}/helpers/{helper_user_id}",
            headers=auth_headers,
        )
        assert r.status_code == 204
        detail = await client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        assert detail.json()["helpers"] == []
