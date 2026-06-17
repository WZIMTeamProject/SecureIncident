from httpx import AsyncClient


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
