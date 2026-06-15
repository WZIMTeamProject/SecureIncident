from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.organization.request import (
    CreateOrganizationRequest,
    CreateInviteRequest,
    JoinByInviteRequest,
)
from api.schemas.organization.response import OrganizationResponse, InviteResponse
from api.schemas.common.base import CreatedIdResponse
from core.config import settings
from db.models.user import User
from services import organization_service


router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: CreateOrganizationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Utwórz organizację (twórca zostaje właścicielem i członkiem)."""
    organization = await organization_service.create_organization(
        db, data=data, current_user=current_user
    )
    return CreatedIdResponse(id=organization.id)


@router.get("", response_model=OrganizationResponse)
async def get_current_organization(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's organization (404 if not a member of any)."""
    organization = await organization_service.get_current_organization(
        db, current_user=current_user
    )
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        description=organization.description,
    )


@router.post("/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    data: CreateInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create organization invitation (organization owner only)."""
    invite, raw_token = await organization_service.create_invite(
        db, data=data, current_user=current_user
    )
    invite_url = f"{settings.FRONTEND_URL}/join?token={raw_token}"
    return InviteResponse(token=raw_token, invite_url=invite_url)


@router.post("/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_organization(
    data: JoinByInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dołącz do organizacji za pomocą tokenu zaproszenia."""
    await organization_service.join_organization(
        db, current_user=current_user, raw_token=data.token
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)