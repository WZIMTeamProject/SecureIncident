from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.invitation.request import CreateInviteRequest, JoinByInviteRequest
from api.schemas.invitation.response import InviteResponse, InvitePreviewResponse
from api.schemas.common.enums import InviteScope
from db.models.user import User


router = APIRouter(tags=["Invitations"])


@router.post("/projects/{project_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_project_invite(
    project_id: str,
    body: CreateInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InviteResponse(token="dummy-invite-token", invite_url=None)


@router.post("/projects/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_project(
    body: JoinByInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.get("/invites/{token}", response_model=InvitePreviewResponse)
async def get_invite_preview(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    return InvitePreviewResponse(
        scope=InviteScope.PROJECT,
        target_name="Test Project",
        is_valid=True,
        expires_at=None,
    )
