import datetime
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.revoked_family import RevokedFamily


async def add_revoked_family(
    db: AsyncSession,
    *,
    family_id: uuid.UUID,
    expires_at: datetime.datetime,
) -> None:
    """Add a rotation family to the denylist (e.g. on reuse detection or logout)."""
    db.add(RevokedFamily(family_id=family_id, expires_at=expires_at))
    await db.flush()


async def is_family_revoked(db: AsyncSession, family_id: uuid.UUID) -> bool:
    """Return True if the rotation family is on the denylist (O(1) PK lookup)."""
    result = await db.scalar(
        select(RevokedFamily.family_id).where(RevokedFamily.family_id == family_id)
    )
    return result is not None


async def cleanup_expired(db: AsyncSession) -> None:
    """Delete revoked-family rows past their expiry timestamp."""
    now_naive = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
    await db.execute(delete(RevokedFamily).where(RevokedFamily.expires_at < now_naive))
    await db.flush()
