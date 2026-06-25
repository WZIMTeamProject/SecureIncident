import uuid
from datetime import UTC, datetime, timedelta

import pytest
from core.security import hash_password
from db.models.incident import Incident
from db.models.incident_helper import IncidentHelper
from db.models.incident_log import IncidentLog
from db.models.organization import Organization
from db.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

NOTIFICATIONS_URL = "/api/incidents/notifications"


def _ts(offset_seconds: int) -> datetime:
    """Naive UTC timestamp helper (project stores naive UTC)."""
    return (datetime.now(UTC) + timedelta(seconds=offset_seconds)).replace(tzinfo=None)


@pytest.fixture
async def actor_user(db: AsyncSession, test_org: Organization) -> User:
    """A second user who performs actions (distinct from test_user)."""
    user = User(
        username=f"actor_{uuid.uuid4().hex[:8]}",
        email=f"actor_{uuid.uuid4().hex[:8]}@example.com",
        first_name="Act",
        last_name="Or",
        password=hash_password("TestPassword123!"),
        is_active=True,
        organization_id=test_org.id,
    )
    db.add(user)
    await db.flush()
    return user


async def _make_log(
    db: AsyncSession,
    *,
    incident_id: uuid.UUID,
    person_id: uuid.UUID,
    log_type: str = "COMMENT",
    comment: str | None = "a comment",
    created_at: datetime | None = None,
) -> IncidentLog:
    log = IncidentLog(
        incident_id=incident_id,
        person_id=person_id,
        type=log_type,
        comment=comment,
    )
    if created_at is not None:
        log.created_at = created_at
    db.add(log)
    await db.flush()
    return log


class TestNotifications:
    async def test_get_notifications_returns_recipient_scoped_logs_newest_first(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_incident: Incident,
        actor_user: User,
        auth_headers: dict[str, str],
    ):
        # test_user is reporter of test_incident; actor_user performs the actions.
        await _make_log(
            db,
            incident_id=test_incident.id,
            person_id=actor_user.id,
            log_type="COMMENT",
            created_at=_ts(-30),
        )
        await _make_log(
            db,
            incident_id=test_incident.id,
            person_id=actor_user.id,
            log_type="ASSIGNEE_CHANGED",
            comment=None,
            created_at=_ts(-10),
        )

        resp = await client.get(NOTIFICATIONS_URL, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2
        timestamps = [item["created_at"] for item in body["items"]]
        assert timestamps == sorted(timestamps, reverse=True)
        assert body["items"][0]["actor_id"] == str(actor_user.id)

    async def test_get_notifications_requires_authentication_returns_401(
        self, client: AsyncClient
    ):
        resp = await client.get(NOTIFICATIONS_URL)
        assert resp.status_code == 401

    async def test_get_notifications_excludes_own_actions(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_incident: Incident,
        test_user: User,
        actor_user: User,
        auth_headers: dict[str, str],
    ):
        # Own action on a connected incident must NOT appear.
        await _make_log(
            db,
            incident_id=test_incident.id,
            person_id=test_user.id,
            log_type="COMMENT",
            created_at=_ts(-20),
        )
        # An action by someone else SHOULD appear.
        await _make_log(
            db,
            incident_id=test_incident.id,
            person_id=actor_user.id,
            log_type="COMMENT",
            created_at=_ts(-10),
        )

        resp = await client.get(NOTIFICATIONS_URL, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        actor_ids = {item["actor_id"] for item in body["items"]}
        assert str(test_user.id) not in actor_ids
        assert str(actor_user.id) in actor_ids

    async def test_get_notifications_excludes_unrelated_incident_logs(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_project,
        actor_user: User,
        auth_headers: dict[str, str],
    ):
        # Incident the test_user is NOT connected to (actor is reporter).
        unrelated = Incident(
            reporter_id=actor_user.id,
            project_id=test_project.id,
            title="Unrelated",
            description="Not connected to test_user",
            status="NEW",
            priority="LOW",
        )
        db.add(unrelated)
        await db.flush()
        await _make_log(
            db,
            incident_id=unrelated.id,
            person_id=actor_user.id,
            log_type="COMMENT",
            created_at=_ts(-10),
        )

        resp = await client.get(NOTIFICATIONS_URL, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["items"] == []

    async def test_get_notifications_includes_helper_connected_incident(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_project,
        test_user: User,
        actor_user: User,
        auth_headers: dict[str, str],
    ):
        # Incident reported by actor; test_user connected ONLY via incident_helpers.
        incident = Incident(
            reporter_id=actor_user.id,
            project_id=test_project.id,
            title="Helper Incident",
            description="test_user is a helper here",
            status="NEW",
            priority="LOW",
        )
        db.add(incident)
        await db.flush()
        db.add(IncidentHelper(incident_id=incident.id, user_id=test_user.id))
        await db.flush()
        await _make_log(
            db,
            incident_id=incident.id,
            person_id=actor_user.id,
            log_type="COMMENT",
            created_at=_ts(-10),
        )

        resp = await client.get(NOTIFICATIONS_URL, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["incident_id"] == str(incident.id)

    async def test_get_notifications_helper_connection_total_is_correct_with_multiple_helpers(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_project,
        test_org: Organization,
        test_user: User,
        actor_user: User,
        auth_headers: dict[str, str],
    ):
        # Multiple helpers on the same incident must NOT multiply the log count.
        incident = Incident(
            reporter_id=actor_user.id,
            project_id=test_project.id,
            title="Multi-helper Incident",
            description="multiple helpers",
            status="NEW",
            priority="LOW",
        )
        db.add(incident)
        await db.flush()

        # test_user is one helper; add two more distinct helpers.
        db.add(IncidentHelper(incident_id=incident.id, user_id=test_user.id))
        for _ in range(2):
            extra = User(
                username=f"helper_{uuid.uuid4().hex[:8]}",
                email=f"helper_{uuid.uuid4().hex[:8]}@example.com",
                first_name="Help",
                last_name="Er",
                password=hash_password("TestPassword123!"),
                is_active=True,
                organization_id=test_org.id,
            )
            db.add(extra)
            await db.flush()
            db.add(IncidentHelper(incident_id=incident.id, user_id=extra.id))
        await db.flush()

        # Exactly 3 distinct logs by the actor.
        for i in range(3):
            await _make_log(
                db,
                incident_id=incident.id,
                person_id=actor_user.id,
                log_type="COMMENT",
                created_at=_ts(-30 + i),
            )

        resp = await client.get(NOTIFICATIONS_URL, headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        # If a join were used, this would be 3 * (number of helpers) = 9.
        assert body["total"] == 3
        assert len(body["items"]) == 3

    async def test_get_notifications_pagination_honors_limit_offset_and_total(
        self,
        client: AsyncClient,
        db: AsyncSession,
        test_incident: Incident,
        actor_user: User,
        auth_headers: dict[str, str],
    ):
        for i in range(5):
            await _make_log(
                db,
                incident_id=test_incident.id,
                person_id=actor_user.id,
                log_type="COMMENT",
                created_at=_ts(-50 + i * 5),
            )

        resp = await client.get(
            NOTIFICATIONS_URL, params={"limit": 2, "offset": 1}, headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert body["limit"] == 2
        assert body["offset"] == 1
        assert len(body["items"]) == 2
