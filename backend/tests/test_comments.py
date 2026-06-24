import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

INCIDENT_ID = "00000000-0000-0000-0000-000000000001"
COMMENTS_URL = f"/api/incidents/{INCIDENT_ID}/comments"


class TestCommentValidation:
    async def test_add_comment_returns_422_when_content_is_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            COMMENTS_URL,
            headers=auth_headers,
            json={"content": ""},
        )
        assert response.status_code == 422

    async def test_add_comment_returns_422_when_content_exceeds_5000_chars(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            COMMENTS_URL,
            headers=auth_headers,
            json={"content": "a" * 5001},
        )
        assert response.status_code == 422

    async def test_add_comment_returns_422_when_content_is_whitespace_only(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            COMMENTS_URL,
            headers=auth_headers,
            json={"content": "   "},
        )
        assert response.status_code == 422


class TestComments:
    async def test_add_comment_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_incident, test_membership
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/comments",
            json={"content": "A comment"},
        )
        assert r.status_code == 401

    async def test_get_comments_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_incident, test_membership
    ):
        r = await client.get(f"/api/incidents/{test_incident.id}/comments")
        assert r.status_code == 401

    async def test_add_comment_returns_403_when_not_reporter_or_assignee(
        self,
        client: AsyncClient,
        test_incident,
        test_membership,
        limited_headers,
        limited_membership,
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/comments",
            json={"content": "A comment"},
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_add_comment_returns_201_when_reporter(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/comments",
            json={"content": "Reporter comment"},
            headers=auth_headers,
        )
        assert r.status_code == 201
        assert "id" in r.json()

    async def test_get_comments_returns_403_when_not_reporter_or_assignee(
        self,
        client: AsyncClient,
        test_incident,
        test_membership,
        limited_headers,
        limited_membership,
    ):
        r = await client.get(
            f"/api/incidents/{test_incident.id}/comments",
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_get_comments_returns_200_with_posted_comment(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        await client.post(
            f"/api/incidents/{test_incident.id}/comments",
            json={"content": "First comment"},
            headers=auth_headers,
        )
        r = await client.get(
            f"/api/incidents/{test_incident.id}/comments",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["comments"]) == 1
        assert data["comments"][0]["content"] == "First comment"
