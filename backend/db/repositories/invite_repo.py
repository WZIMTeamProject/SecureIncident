from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.organization_invite import OrganizationInvite


def _to_naive_utc(expires_at: datetime | None) -> datetime | None:
    """Normalize an expiry to UTC-naive for storage (naive input is treated as UTC)."""
    if expires_at is None:
        return None
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at.astimezone(UTC).replace(tzinfo=None)


async def create_project_invite(
    db: AsyncSession,
    *,
    project_id: UUID,
    created_by_id: UUID,
    token_hash: str,
    role_id: UUID,
    expires_at: datetime | None,
    max_uses: int | None,
) -> OrganizationInvite:
    """Create project invitation (save token hash)."""
    invite = OrganizationInvite(
        scope="PROJECT",
        project_id=project_id,
        organization_id=None,
        created_by_id=created_by_id,
        token=token_hash,
        role_id=role_id,
        expires_at=_to_naive_utc(expires_at),
        max_uses=max_uses,
        use_count=0,
    )
    db.add(invite)
    await db.flush()
    return invite


async def create_organization_invite(
    db: AsyncSession,
    *,
    organization_id: UUID,
    created_by_id: UUID,
    token_hash: str,
    expires_at: datetime | None,
    max_uses: int | None,
) -> OrganizationInvite:
    """Create organization invitation (scope=ORGANIZATION, no role).

    Organization has no roles (roles are per-project), so role_id=None.
    """
    invite = OrganizationInvite(
        scope="ORGANIZATION",
        organization_id=organization_id,
        project_id=None,
        role_id=None,
        created_by_id=created_by_id,
        token=token_hash,
        expires_at=_to_naive_utc(expires_at),
        max_uses=max_uses,
        use_count=0,
    )
    db.add(invite)
    await db.flush()
    return invite


async def get_invite_by_hash(
    db: AsyncSession, token_hash: str
) -> OrganizationInvite | None:
    """Get invitation by token hash (eager-load project + organization)."""
    result = await db.execute(
        select(OrganizationInvite)
        .options(
            selectinload(OrganizationInvite.project),
            selectinload(OrganizationInvite.organization),
        )
        .where(OrganizationInvite.token == token_hash)
    )
    return result.scalar_one_or_none()


async def get_and_increment_invite(
    db: AsyncSession, token_hash: str
) -> OrganizationInvite | None:
    """Atomically get invitation and increment use_count (in single transaction)."""
    now = datetime.now(UTC).replace(tzinfo=None)
    result = await db.execute(
        update(OrganizationInvite)
        .where(
            OrganizationInvite.token == token_hash,
            or_(
                OrganizationInvite.expires_at == None,
                OrganizationInvite.expires_at > now,
            ),
            or_(
                OrganizationInvite.max_uses == None,
                OrganizationInvite.use_count < OrganizationInvite.max_uses,
            ),
        )
        .values(use_count=OrganizationInvite.use_count + 1)
        .returning(OrganizationInvite)
    )
    return result.scalar_one_or_none()


async def delete_invite_by_hash(db: AsyncSession, token_hash: str) -> bool:
    """Hard-delete invite by token hash. Returns True if deleted, False if not found."""
    result = await db.execute(
        delete(OrganizationInvite).where(OrganizationInvite.token == token_hash)
    )
    await db.flush()
    return result.rowcount > 0
