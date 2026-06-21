from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.invitation.request import CreateInviteRequest, JoinByInviteRequest
from api.schemas.invitation.response import InviteResponse, InvitePreviewResponse
from db.models.user import User
from services import invitation_service
from core.config import settings

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
    await invitation_service.revoke_invite(db, raw_token=token, current_user=current_user)
    return Response(status_code=204)
