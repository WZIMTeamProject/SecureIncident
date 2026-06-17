import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.invitation.request import CreateInviteRequest, JoinByInviteRequest
from api.schemas.invitation.response import InviteResponse, InvitePreviewResponse
from api.schemas.common.enums import InviteScope
from db.models.user import User
from services import invitation_service
from core.config import settings
from db import repositories
from core import security

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Invitations"])


@router.post("/projects/{project_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_project_invite(
    project_id: UUID,
    body: CreateInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invite, raw_token = await invitation_service.create_project_invite(
        db, project_id=project_id, created_by=current_user, data=body
    )
    return InviteResponse(
        token=raw_token,
        invite_url=f"{settings.FRONTEND_URL}/invites/{raw_token}"
    )


@router.post("/projects/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_project(
    body: JoinByInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await invitation_service.join_project_by_invite(
        db, current_user=current_user, raw_token=body.token
    )
    return Response(status_code=204)


@router.get("/invites/{token}", response_model=InvitePreviewResponse)
async def get_invite_preview(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    return await invitation_service.get_invite_preview(db, raw_token=token)


@router.delete("/invites/{token}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_invite(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    token_hash = security.hash_token(token)
    invite = await repositories.invite_repo.get_invite_by_hash(db, token_hash)
    if invite is None:
        logger.warning("Invite revoke failed: not found user_id=%s", current_user.id)
        raise HTTPException(status_code=404, detail="Invite not found")

    is_creator = invite.created_by_id == current_user.id
    is_project_owner = (
        invite.project is not None
        and invite.project.project_owner_id == current_user.id
    )
    is_org_owner = (
        invite.organization is not None
        and invite.organization.org_owner_id == current_user.id
    )
    if not (is_creator or is_project_owner or is_org_owner):
        logger.warning("Invite revoke denied: permission denied user_id=%s", current_user.id)
        raise HTTPException(status_code=403, detail="Not authorized to revoke this invite")

    await repositories.invite_repo.delete_invite_by_hash(db, token_hash)
    await db.commit()
    return Response(status_code=204)
