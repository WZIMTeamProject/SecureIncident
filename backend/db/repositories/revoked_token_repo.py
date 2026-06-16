import datetime
import uuid
from datetime import timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.revoked_token import RevokedToken


async def is_token_revoked(db: AsyncSession, jti: str) -> bool:
    """Sprawdza, czy token o danym JTI znajduje się na czarnej liście."""
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
    """Dodaje token do czarnej listy po wylogowaniu."""
    db.add(RevokedToken(jti=jti, user_id=user_id, expires_at=expires_at))
    await db.commit()


async def cleanup_expired_revoked_tokens(db: AsyncSession) -> None:
    """Usuwa z bazy tokeny, których czas ważności (exp) już minął."""
    now_naive = datetime.datetime.now(timezone.utc).replace(tzinfo=None)
    await db.execute(
        delete(RevokedToken).where(RevokedToken.expires_at < now_naive)
    )