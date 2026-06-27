"""TDD red-gate tests for access + refresh token rotation (RFC 9700, Option C).

These tests describe the target behavior and MUST fail before implementation:
- login must advertise the access-token TTL via `expires_in` (Option A cheap fix)
- login must set a refresh token in an HttpOnly cookie scoped to the refresh path
- POST /api/auth/refresh must mint a new access token and rotate the refresh cookie

They are the executable specification of the feature's core contract.
"""

import re
import uuid
from datetime import UTC, datetime, timedelta

from core import security
from core.config import settings
from db import repositories
from db.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

COOKIE = settings.REFRESH_COOKIE_NAME


def _login_payload(username: str, *, remember: bool = False) -> dict:
    return {
        "username": username,
        "password": "TestPassword123!",
        "remember_user": remember,
    }


def _max_age(set_cookie_header: str) -> int | None:
    """Extract the Max-Age value from a (joined) Set-Cookie header string."""
    match = re.search(r"[Mm]ax-[Aa]ge=(\d+)", set_cookie_header)
    return int(match.group(1)) if match else None


class TestLoginAdvertisesExpiry:
    async def test_login_response_includes_expires_in_seconds(
        self, client: AsyncClient, test_user: User
    ):
        """Option A: client must be able to derive cookie Max-Age from the response."""
        response = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        assert response.status_code == 200
        data = response.json()
        assert "expires_in" in data, "LoginResponse must expose access-token TTL"
        # 15-minute access token => ~900 seconds.
        assert 600 < data["expires_in"] <= 1800

    async def test_login_access_token_ttl_is_about_15_minutes(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        token = response.json()["access_token"]
        payload = security.decode_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        ttl_minutes = (exp - datetime.now(UTC)).total_seconds() / 60
        assert 10 < ttl_minutes < 20


class TestLoginSetsRefreshCookie:
    async def test_login_sets_httponly_refresh_cookie(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        set_cookie = " ".join(response.headers.get_list("set-cookie"))
        assert "refresh_token=" in set_cookie, "login must set a refresh_token cookie"
        assert "HttpOnly" in set_cookie


class TestRefreshEndpoint:
    async def test_refresh_issues_new_access_token(
        self, client: AsyncClient, test_user: User
    ):
        login = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        original_access = login.json()["access_token"]

        # httpx AsyncClient carries the refresh cookie set by login.
        refresh = await client.post("/api/auth/refresh")
        assert refresh.status_code == 200
        data = refresh.json()
        assert "access_token" in data
        assert data["access_token"] != original_access

    async def test_refresh_rotates_the_refresh_cookie(
        self, client: AsyncClient, test_user: User
    ):
        await client.post("/api/auth/login", json=_login_payload(test_user.username))
        refresh = await client.post("/api/auth/refresh")
        rotated = " ".join(refresh.headers.get_list("set-cookie"))
        assert "refresh_token=" in rotated, "refresh must rotate (re-set) the cookie"

    async def test_refresh_without_cookie_returns_401(self, client: AsyncClient):
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 401


class TestRefreshRotationChain:
    async def test_second_refresh_issues_new_token_and_rotates_cookie(
        self, client: AsyncClient, test_user: User
    ):
        """Rotation must chain: a second refresh consumes the rotated cookie,
        returns a fresh access token and re-sets the refresh cookie again."""
        await client.post("/api/auth/login", json=_login_payload(test_user.username))

        first = await client.post("/api/auth/refresh")
        assert first.status_code == 200
        first_access = first.json()["access_token"]

        second = await client.post("/api/auth/refresh")
        assert second.status_code == 200
        second_access = second.json()["access_token"]

        assert second_access != first_access
        rotated = " ".join(second.headers.get_list("set-cookie"))
        assert f"{COOKIE}=" in rotated, "second refresh must re-set the cookie"


class TestRefreshReuseDetection:
    async def test_replaying_old_cookie_revokes_family(
        self, client: AsyncClient, test_user: User
    ):
        """Replaying a consumed refresh token triggers reuse detection: the old
        token is rejected AND the whole family (incl. the now-current token) dies."""
        login = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        old_cookie = login.cookies.get(COOKIE)

        rotated = await client.post("/api/auth/refresh")
        assert rotated.status_code == 200
        current_cookie = rotated.cookies.get(COOKIE)

        # Replay the OLD (already-consumed) cookie -> reuse detection -> 401.
        client.cookies.clear()
        client.cookies.set(COOKIE, old_cookie, domain="test", path="/api/auth/refresh")
        replay = await client.post("/api/auth/refresh")
        assert replay.status_code == 401

        # The previously-valid current cookie is now dead (family revoked).
        client.cookies.clear()
        client.cookies.set(
            COOKIE, current_cookie, domain="test", path="/api/auth/refresh"
        )
        followup = await client.post("/api/auth/refresh")
        assert followup.status_code == 401


class TestRefreshExpiry:
    async def test_expired_refresh_row_returns_401(
        self, client: AsyncClient, db: AsyncSession, test_user: User
    ):
        """A refresh token whose stored row is already past expiry -> 401."""
        raw = security.generate_token()
        past = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=1)
        await repositories.refresh_token_repo.create_refresh_token(
            db,
            token_hash=security.hash_token(raw),
            family_id=uuid.uuid4(),
            user_id=test_user.id,
            expires_at=past,
        )
        await db.flush()

        client.cookies.set(COOKIE, raw, domain="test", path="/api/auth/refresh")
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 401


class TestRememberMeCookieLifetime:
    async def test_remember_me_extends_refresh_cookie_but_not_access_token(
        self, client: AsyncClient, test_user: User
    ):
        """remember_user lengthens the refresh cookie Max-Age (~30 days) while the
        access token stays short-lived (~15 min)."""
        response = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username, remember=True)
        )
        assert response.status_code == 200

        set_cookie = " ".join(response.headers.get_list("set-cookie"))
        max_age = _max_age(set_cookie)
        assert max_age is not None, "refresh cookie must carry a Max-Age"
        # ~30 days; comfortably above the 1-day non-remember default.
        assert max_age > 25 * 24 * 3600

        token = response.json()["access_token"]
        payload = security.decode_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        ttl_minutes = (exp - datetime.now(UTC)).total_seconds() / 60
        assert 10 < ttl_minutes < 20


class TestLogoutClearsRefresh:
    async def test_logout_then_refresh_returns_401(
        self, client: AsyncClient, test_user: User
    ):
        login = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        access_token = login.json()["access_token"]

        logout = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout.status_code == 204

        refresh = await client.post("/api/auth/refresh")
        assert refresh.status_code == 401


class TestTokenTypeConfusion:
    """The opaque-vs-JWT split must hold in BOTH directions.

    Refresh tokens are random opaque values stored as hashes; access tokens are
    signed JWTs. Neither artifact may stand in for the other — a refresh token
    must not authenticate a protected endpoint, and an access JWT must not pass
    as a refresh cookie. (security.md: opaque/JWT separation invariant.)
    """

    async def test_raw_refresh_token_cannot_authenticate_as_bearer(
        self, client: AsyncClient, test_user: User
    ):
        """A raw refresh-token value sent as `Authorization: Bearer` -> 401.

        The opaque refresh value is not a signed JWT, so access-token validation
        rejects it; it must never grant access to a protected endpoint.
        """
        login = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        raw_refresh = login.cookies.get(COOKIE)
        assert raw_refresh is not None

        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {raw_refresh}"},
        )
        assert response.status_code == 401

    async def test_access_jwt_presented_as_refresh_cookie_returns_401(
        self, client: AsyncClient, test_user: User
    ):
        """An access JWT placed in the refresh cookie -> 401 at /refresh.

        The JWT's SHA-256 hash matches no stored refresh-token row, so rotation
        rejects it. Covers the unknown-token (row is None) branch of refresh.
        """
        login = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        access_token = login.json()["access_token"]

        client.cookies.clear()
        client.cookies.set(
            COOKIE, access_token, domain="test", path="/api/auth/refresh"
        )
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 401


class TestRotationDoesNotExtendFamilyLifetime:
    async def test_rotated_cookie_max_age_not_greater_than_original(
        self, client: AsyncClient, test_user: User
    ):
        """Rotation carries the family's absolute expiry forward, never extending it.

        The rotated cookie's Max-Age must be <= the original (it shrinks by the
        elapsed time), proving a stolen-token rotation loop cannot keep a family
        alive indefinitely.
        """
        login = await client.post(
            "/api/auth/login", json=_login_payload(test_user.username)
        )
        original_max_age = _max_age(" ".join(login.headers.get_list("set-cookie")))
        assert original_max_age is not None

        refresh = await client.post("/api/auth/refresh")
        assert refresh.status_code == 200
        rotated_max_age = _max_age(" ".join(refresh.headers.get_list("set-cookie")))
        assert rotated_max_age is not None

        assert rotated_max_age <= original_max_age
