import logging
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.invitation.request import CreateInviteRequest
from api.schemas.invitation.response import InviteResponse, InvitePreviewResponse
from core import security
from db.models.organization_invite import OrganizationInvite
from db.models.user import User
from db import repositories

logger = logging.getLogger(__name__)


async def create_project_invite(
    db: AsyncSession,
    *,
    project_id: UUID,
    created_by: User,
    data: CreateInviteRequest,
) -> tuple[OrganizationInvite, str]:
    """Create project invitation."""
    # 1. Check if project exists
    project = await repositories.invite_repo.get_project_by_id(db, project_id)
    if project is None:
        logger.warning(
            "Invite creation failed: project not found project_id=%s user_id=%s",
            project_id,
            created_by.id,
        )
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Check if current user is project owner
    if project.project_owner_id != created_by.id:
        logger.warning(
            "Invite creation failed: permission denied user_id=%s project_id=%s",
            created_by.id,
            project_id,
        )
        raise HTTPException(
            status_code=403, detail="Only project owner can create invitations"
        )

    # 3. Check if role exists and belongs to this project
    role = await repositories.invite_repo.get_role_by_id(db, data.role_id)
    if role is None:
        logger.warning(
            "Invite creation failed: role not found role_id=%s project_id=%s",
            data.role_id,
            project_id,
        )
        raise HTTPException(status_code=404, detail="Role not found")
    if role.project_id != project_id:
        logger.warning(
            "Invite creation failed: role not in project role_id=%s project_id=%s",
            data.role_id,
            project_id,
        )
        raise HTTPException(status_code=400, detail="This role does not exist in this project")

    # 4. Generate token
    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)

    # 5. Save invitation
    invite = await repositories.invite_repo.create_project_invite(
        db,
        project_id=project_id,
        created_by_id=created_by.id,
        token_hash=token_hash,
        role_id=data.role_id,
        expires_at=data.expires_at,
        max_uses=data.max_uses,
    )
    await db.commit()
    await db.refresh(invite)
    logger.info(
        "Project invite created invite_id=%s project_id=%s user_id=%s",
        invite.id,
        project_id,
        created_by.id,
    )
    return invite, raw_token


async def get_invite_preview(db: AsyncSession, raw_token: str) -> InvitePreviewResponse:
    """Get invitation preview (public, no authentication required)."""
    token_hash = security.hash_token(raw_token)
    invite = await repositories.invite_repo.get_invite_by_hash(db, token_hash)

    if invite is None:
        logger.warning("Invite preview failed: invitation not found")
        raise HTTPException(status_code=404, detail="Invitation not found")

    is_valid = _is_invite_valid(invite)
    target_name = (
        invite.project.name if invite.scope == "PROJECT" and invite.project else invite.organization.name
    )

    return InvitePreviewResponse(
        scope=invite.scope,
        target_name=target_name,
        is_valid=is_valid,
        expires_at=invite.expires_at,
    )


async def join_project_by_invite(
    db: AsyncSession,
    *,
    current_user: User,
    raw_token: str,
) -> None:
    """Join project using invitation."""
    token_hash = security.hash_token(raw_token)

    # Read-only pre-check: validate scope and org membership BEFORE consuming a use slot.
    # This prevents a cross-org user from draining limited-use invites with repeated 403s.
    pre_check = await repositories.invite_repo.get_invite_by_hash(db, token_hash)
    if pre_check is None:
        logger.warning("Project join failed: invitation not found user_id=%s", current_user.id)
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")

    if pre_check.scope != "PROJECT":
        logger.warning(
            "Project join failed: wrong invitation scope=%s user_id=%s",
            pre_check.scope,
            current_user.id,
        )
        raise HTTPException(status_code=400, detail="This invitation is not for a project")

    if pre_check.project is not None and pre_check.project.organization_id is not None:
        if current_user.organization_id != pre_check.project.organization_id:
            logger.warning(
                "Project join failed: org mismatch user_id=%s user_org_id=%s required_org_id=%s",
                current_user.id,
                current_user.organization_id,
                pre_check.project.organization_id,
            )
            raise HTTPException(
                status_code=403,
                detail="You must be a member of this organization to join its projects"
            )

    # Atomic increment — only after scope and auth checks pass
    invite = await repositories.invite_repo.get_and_increment_invite(db, token_hash)
    if invite is None:
        logger.warning(
            "Project join failed: invitation exhausted or expired user_id=%s",
            current_user.id,
        )
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")

    # Check if user is already member
    existing = await repositories.invite_repo.get_user_project(
        db, current_user.id, invite.project_id
    )
    if existing is not None:
        logger.warning(
            "Project join failed: already member user_id=%s project_id=%s",
            current_user.id,
            invite.project_id,
        )
        raise HTTPException(status_code=409, detail="You are already a member of this project")

    # Create membership
    await repositories.invite_repo.create_user_project(
        db,
        user_id=current_user.id,
        project_id=invite.project_id,
        role_id=invite.role_id,
    )

    await db.commit()
    logger.info(
        "User joined project via invite user_id=%s project_id=%s",
        current_user.id,
        invite.project_id,
    )


def _is_invite_valid(invite: OrganizationInvite) -> bool:
    """Helper: check if invitation is valid (not expired, not exhausted)."""
    if invite.expires_at is not None:
        if datetime.now(timezone.utc).replace(tzinfo=None) > invite.expires_at:
            return False
    if invite.max_uses is not None:
        if invite.use_count >= invite.max_uses:
            return False
    return True