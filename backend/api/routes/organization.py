from core.config import settings
from db.models.user import User
from fastapi import APIRouter, Depends, Response, status
from services import organization_service
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.schemas.common.base import CreatedIdResponse, DetailResponse
from api.schemas.organization.request import (
    CreateInviteRequest,
    CreateOrganizationRequest,
    JoinByInviteRequest,
)
from api.schemas.organization.response import InviteResponse, OrganizationResponse

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: CreateOrganizationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create organization. Creator becomes owner; user may belong to only one org."""
    organization = await organization_service.create_organization(
        db, data=data, current_user=current_user
    )
    return CreatedIdResponse(id=organization.id)


@router.get("", response_model=OrganizationResponse)
async def get_current_organization(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return current user's organization (404 if not a member of any)."""
    organization = await organization_service.get_current_organization(
        db, current_user=current_user
    )
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        description=organization.description,
    )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": DetailResponse,
            "description": "Not authenticated (missing, invalid, expired or revoked token).",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": DetailResponse,
            "description": "Only the organization owner can delete the organization.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": DetailResponse,
            "description": "User does not belong to any organization, or the organization was not found.",
        },
    },
)
async def delete_organization(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete the current user's organization (organization owner only)."""
    await organization_service.delete_organization(db, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED
)
async def create_invite(
    data: CreateInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create organization invitation (organization owner only). Returns one-time raw token."""
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
    """Join organization via invite. Fails with 409 if user already belongs to an org."""
    await organization_service.join_organization(
        db, current_user=current_user, raw_token=data.token
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
