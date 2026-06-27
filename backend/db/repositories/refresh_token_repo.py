import datetime
import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.refresh_token import RefreshToken


async def create_refresh_token(
    db: AsyncSession,
    *,
    token_hash: str,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    expires_at: datetime.datetime,
) -> RefreshToken:
    """Persist a refresh token (stored as a hash) for a rotation family."""
    row = RefreshToken(
        token_hash=token_hash,
        family_id=family_id,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(row)
    await db.flush()
    return row


async def get_by_hash(db: AsyncSession, token_hash: str) -> RefreshToken | None:
    """Look up a refresh token by its stored hash."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return result.scalar_one_or_none()


async def mark_used(db: AsyncSession, token_id: uuid.UUID) -> bool:
    """Atomically consume a refresh token during rotation.

    The conditional ``WHERE used == False`` is the race-safe guard: under READ
    COMMITTED two concurrent refreshes both read ``used=False``, but only one
    UPDATE can flip the row — the loser blocks on the row lock, re-evaluates the
    predicate after the winner commits, and affects zero rows. Returns True when
    this call consumed the token; False means it was already consumed (replay).
    """
    result = await db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == token_id, RefreshToken.used == False)
        .values(used=True)
    )
    await db.flush()
    return result.rowcount == 1


async def revoke_family(db: AsyncSession, family_id: uuid.UUID) -> None:
    """Delete every refresh token belonging to a rotation family.

    Hygiene only: revoked_families is the authoritative family-revoked signal.
    """
    await db.execute(delete(RefreshToken).where(RefreshToken.family_id == family_id))
    await db.flush()


async def cleanup_expired(db: AsyncSession) -> None:
    """Delete refresh tokens past their expiry timestamp."""
    now_naive = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    await db.execute(delete(RefreshToken).where(RefreshToken.expires_at < now_naive))
    await db.flush()
