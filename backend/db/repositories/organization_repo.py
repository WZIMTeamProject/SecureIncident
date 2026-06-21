from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.organization import Organization


async def get_organization_by_id(
    db: AsyncSession, organization_id: UUID
) -> Optional[Organization]:
    """Get organization by ID."""
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    return result.scalar_one_or_none()


async def create_organization(
    db: AsyncSession,
    *,
    name: str,
    description: Optional[str],
    owner_id: UUID,
) -> Organization:
    """Create organization (flush only — commit in service, multi-step flow)."""
    organization = Organization(
        name=name,
        description=description,
        org_owner_id=owner_id,
    )
    db.add(organization)
    await db.flush()  # assign ID but do not commit — service commits entire transaction
    return organization


async def delete_organization(db: AsyncSession, organization_id: UUID) -> None:
    """Hard-delete an organization by ID.

    Relies on DB-level ON DELETE rules defined on the models:
      - users.organization_id                 -> SET NULL (members detached)
      - projects.organization_id              -> SET NULL (projects orphaned)
      - organization_invites.organization_id  -> CASCADE  (org invites removed)

    Flush only — the calling service commits the whole transaction.
    """
    await db.execute(delete(Organization).where(Organization.id == organization_id))
    await db.flush()