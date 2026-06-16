from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, or_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.organization_invite import OrganizationInvite
from db.repositories.project_repo import ( # Methods invoked by invitation_service.py. Imported in order to not duplicate code.
    get_project_by_id,
    get_role_by_id,
    get_user_project,
    create_user_project,
)


async def create_project_invite(
    db: AsyncSession,
    *,
    project_id: UUID,
    created_by_id: UUID,
    token_hash: str,
    role_id: UUID,
    expires_at: Optional[datetime],
    max_uses: Optional[int],
) -> OrganizationInvite:
    """Utwórz zaproszenie do projektu (zapisz hasz tokenu)."""
    invite = OrganizationInvite(
        scope="PROJECT",
        project_id=project_id,
        organization_id=None,
        created_by_id=created_by_id,
        token=token_hash,
        role_id=role_id,
        expires_at=expires_at.replace(tzinfo=None) if expires_at is not None else None,
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
    expires_at: Optional[datetime],
    max_uses: Optional[int],
) -> OrganizationInvite:
    """Utwórz zaproszenie do organizacji (scope=ORGANIZATION, bez roli).

    Organizacja nie ma ról (role są per-projekt), więc role_id=None.
    """
    invite = OrganizationInvite(
        scope="ORGANIZATION",
        organization_id=organization_id,
        project_id=None,
        role_id=None,
        created_by_id=created_by_id,
        token=token_hash,
        expires_at=expires_at.replace(tzinfo=None) if expires_at is not None else None,
        max_uses=max_uses,
        use_count=0,
    )
    db.add(invite)
    await db.flush()
    return invite


async def get_invite_by_hash(db: AsyncSession, token_hash: str) -> Optional[OrganizationInvite]:
    """Pobierz zaproszenie po hashu tokenu (eager-load project + organization)."""
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
) -> Optional[OrganizationInvite]:
    """Atomowo pobierz zaproszenie i zwiększ use_count (w jednej transakcji)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
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