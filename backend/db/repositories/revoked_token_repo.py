import datetime
import uuid
from datetime import timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.revoked_token import RevokedToken


async def is_token_revoked(db: AsyncSession, jti: str) -> bool:
    """Check whether the token with the given JTI is on the revocation list."""
    result = await db.scalar(
        select(RevokedToken.id).where(RevokedToken.jti == jti)
    )
    return result is not None


async def add_revoked_token(
    db: AsyncSession,
    *,
    jti: str,
    user_id: uuid.UUID,
    expires_at: datetime.datetime,
) -> None:
    """Add the token to the revocation list after logout."""
    db.add(RevokedToken(jti=jti, user_id=user_id, expires_at=expires_at))
    await db.flush()


async def cleanup_expired_revoked_tokens(db: AsyncSession) -> None:
    """Delete expired tokens (past their exp timestamp) from the database."""
    now_naive = datetime.datetime.now(timezone.utc).replace(tzinfo=None)
    await db.execute(
        delete(RevokedToken).where(RevokedToken.expires_at < now_naive)
    )
    await db.flush()