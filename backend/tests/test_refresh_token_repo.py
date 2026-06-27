import uuid
from datetime import UTC, datetime, timedelta

from db.repositories import refresh_token_repo, revoked_family_repo
from sqlalchemy.ext.asyncio import AsyncSession


def _future() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None) + timedelta(days=7)


class TestRefreshTokenRepo:
    async def test_create_and_get_by_hash_round_trips_row(
        self, db: AsyncSession, test_user
    ):
        family_id = uuid.uuid4()
        row = await refresh_token_repo.create_refresh_token(
            db,
            token_hash="hash-abc",
            family_id=family_id,
            user_id=test_user.id,
            expires_at=_future(),
        )

        fetched = await refresh_token_repo.get_by_hash(db, "hash-abc")

        assert fetched is not None
        assert fetched.id == row.id
        assert fetched.token_hash == "hash-abc"
        assert fetched.family_id == family_id
        assert fetched.user_id == test_user.id
        assert fetched.used is False

    async def test_get_by_hash_returns_none_for_unknown_hash(self, db: AsyncSession):
        assert await refresh_token_repo.get_by_hash(db, "does-not-exist") is None

    async def test_mark_used_flips_used_to_true(self, db: AsyncSession, test_user):
        row = await refresh_token_repo.create_refresh_token(
            db,
            token_hash="hash-mark",
            family_id=uuid.uuid4(),
            user_id=test_user.id,
            expires_at=_future(),
        )
        assert row.used is False

        claimed = await refresh_token_repo.mark_used(db, row.id)

        assert claimed is True
        refetched = await refresh_token_repo.get_by_hash(db, "hash-mark")
        assert refetched is not None
        assert refetched.used is True

    async def test_mark_used_is_single_use_second_claim_returns_false(
        self, db: AsyncSession, test_user
    ):
        # C-1 guard: the conditional UPDATE consumes the token exactly once, so a
        # second (concurrent or replayed) claim affects zero rows and returns False.
        row = await refresh_token_repo.create_refresh_token(
            db,
            token_hash="hash-once",
            family_id=uuid.uuid4(),
            user_id=test_user.id,
            expires_at=_future(),
        )

        first = await refresh_token_repo.mark_used(db, row.id)
        second = await refresh_token_repo.mark_used(db, row.id)

        assert first is True
        assert second is False

    async def test_revoke_family_affects_only_target_family(
        self, db: AsyncSession, test_user
    ):
        target_family = uuid.uuid4()
        other_family = uuid.uuid4()
        await refresh_token_repo.create_refresh_token(
            db,
            token_hash="target-1",
            family_id=target_family,
            user_id=test_user.id,
            expires_at=_future(),
        )
        await refresh_token_repo.create_refresh_token(
            db,
            token_hash="other-1",
            family_id=other_family,
            user_id=test_user.id,
            expires_at=_future(),
        )

        await refresh_token_repo.revoke_family(db, target_family)

        assert await refresh_token_repo.get_by_hash(db, "target-1") is None
        assert await refresh_token_repo.get_by_hash(db, "other-1") is not None

    async def test_revoked_family_round_trips_and_unknown_is_false(
        self, db: AsyncSession
    ):
        family_id = uuid.uuid4()
        assert await revoked_family_repo.is_family_revoked(db, family_id) is False

        await revoked_family_repo.add_revoked_family(
            db, family_id=family_id, expires_at=_future()
        )

        assert await revoked_family_repo.is_family_revoked(db, family_id) is True
        assert await revoked_family_repo.is_family_revoked(db, uuid.uuid4()) is False
