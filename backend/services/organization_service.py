import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.organization.request import (
    CreateOrganizationRequest,
    CreateInviteRequest,
)
from core import security
from db.models.organization import Organization
from db.models.organization_invite import OrganizationInvite
from db.models.user import User
from db import repositories

logger = logging.getLogger(__name__)


async def create_organization(
    db: AsyncSession,
    *,
    data: CreateOrganizationRequest,
    current_user: User,
) -> Organization:
    """Create organization and set creator as owner + member.

    Domain rule: a user can belong to only ONE organization.
    If already member of one, cannot create another.
    """
    if current_user.organization_id is not None:
        logger.warning(
            "Organization creation failed: user already belongs to an org user_id=%s",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to an organization",
        )

    organization = await repositories.organization_repo.create_organization(
        db,
        name=data.name.strip(),
        description=data.description,
        owner_id=current_user.id,
    )

    # Creator becomes member of their organization (same session — mutation is tracked).
    current_user.organization_id = organization.id
    db.add(current_user)

    await db.commit()
    await db.refresh(organization)
    return organization


async def get_current_organization(
    db: AsyncSession,
    *,
    current_user: User,
) -> Organization:
    """Return current user's organization (404 if not a member of any)."""
    if current_user.organization_id is None:
        logger.warning(
            "Organization fetch failed: user has no organization user_id=%s",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not belong to any organization",
        )

    organization = await repositories.organization_repo.get_organization_by_id(
        db, current_user.organization_id
    )
    if organization is None:
        logger.warning(
            "Organization fetch failed: record not found org_id=%s",
            current_user.organization_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    return organization


async def create_invite(
    db: AsyncSession,
    *,
    data: CreateInviteRequest,
    current_user: User,
) -> tuple[OrganizationInvite, str]:
    """Create organization invitation (organization owner only).

    Returns (invite, raw_token). Only token hash is stored in database —
    raw token is only returned to caller and cannot be recovered later.
    """
    if current_user.organization_id is None:
        logger.warning(
            "Invite creation failed: user has no organization user_id=%s",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not belong to any organization",
        )

    organization = await repositories.organization_repo.get_organization_by_id(
        db, current_user.organization_id
    )
    if organization is None:
        logger.warning(
            "Invite creation failed: organization not found org_id=%s",
            current_user.organization_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if organization.org_owner_id != current_user.id:
        logger.warning(
            "Invite creation failed: permission denied user_id=%s org_id=%s",
            current_user.id,
            organization.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can create invitations",
        )

    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)

    invite = await repositories.invite_repo.create_organization_invite(
        db,
        organization_id=organization.id,
        created_by_id=current_user.id,
        token_hash=token_hash,
        expires_at=data.expires_at,
        max_uses=data.max_uses,
    )
    await db.commit()
    await db.refresh(invite)

    return invite, raw_token


async def join_organization(
    db: AsyncSession,
    *,
    current_user: User,
    raw_token: str,
) -> None:
    """Join organization using invitation token.

    Domain rule: user can belong to only one organization —
    if already member of one, return 409 (before consuming invitation).
    """
    if current_user.organization_id is not None:
        logger.warning("Join organization failed: user already has org user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to an organization",
        )

    token_hash = security.hash_token(raw_token)

    # Atomic use_count increment — only if invitation is valid.
    invite = await repositories.invite_repo.get_and_increment_invite(db, token_hash)
    if invite is None:
        logger.warning(
            "Join organization failed: invalid or expired invitation user_id=%s",
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invitation",
        )

    if invite.scope != "ORGANIZATION" or invite.organization_id is None:
        logger.warning(
            "Join organization failed: invitation not for organization scope=%s user_id=%s",
            invite.scope,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invitation is not for an organization",
        )

    current_user.organization_id = invite.organization_id
    db.add(current_user)
    await db.commit()