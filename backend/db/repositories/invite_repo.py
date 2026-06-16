from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, or_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.organization_invite import OrganizationInvite
from db.models.user_project import UserProject
from db.models.project import Project
from db.models.role import Role


async def get_project_by_id(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    """Pobierz projekt po ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def get_role_by_id(db: AsyncSession, role_id: UUID) -> Optional[Role]:
    """Pobierz rolę po ID."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    return result.scalar_one_or_none()


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
    await db.commit()
    await db.refresh(invite)
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
    Pojedynczy zapis — commit tutaj, analogicznie do create_project_invite.
    """
    invite = OrganizationInvite(
        scope="ORGANIZATION",
        organization_id=organization_id,
        project_id=None,
        role_id=None,
        created_by_id=created_by_id,
        token=token_hash,
        expires_at=expires_at,
        max_uses=max_uses,
        use_count=0,
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
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
    now = datetime.now()
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


async def get_user_project(
    db: AsyncSession, user_id: UUID, project_id: UUID
) -> Optional[UserProject]:
    """Sprawdź czy użytkownik jest już członkiem projektu."""
    result = await db.execute(
        select(UserProject).where(
            UserProject.user_id == user_id,
            UserProject.project_id == project_id,
        )
    )
    return result.scalar_one_or_none()


async def create_user_project(
    db: AsyncSession,
    *,
    user_id: UUID,
    project_id: UUID,
    role_id: UUID,
) -> UserProject:
    """Utwórz członkostwo użytkownika w projekcie (flush tylko, bez commita)."""
    membership = UserProject(
        user_id=user_id,
        project_id=project_id,
        role_id=role_id,
    )
    db.add(membership)
    await db.flush()  # flush do DB ale nie commituj — commit w serwisie
    return membership


async def delete_invite_by_hash(db: AsyncSession, token_hash: str) -> bool:
    """Hard-delete invite by token hash. Returns True if deleted, False if not found."""
    result = await db.execute(
        delete(OrganizationInvite).where(OrganizationInvite.token == token_hash)
    )
    await db.commit()
    return result.rowcount > 0