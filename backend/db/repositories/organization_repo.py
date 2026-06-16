from typing import Optional
from uuid import UUID

from sqlalchemy import select
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
