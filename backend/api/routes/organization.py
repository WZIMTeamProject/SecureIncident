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
from db.models.user import User


router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: CreateOrganizationRequest,
    db: AsyncSession = Depends(get_db),
):
    # TODO: stworzyć organizację, przypisać ownera
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("", response_model=OrganizationResponse)
async def get_current_organization(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: zwrócić organizację użytkownika (jeśli jest przypisany, inaczej 404)
    return OrganizationResponse(
        id="00000000-0000-0000-0000-000000000000",
        name="Test Organization",
        description="Test description",
    )


@router.post("/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    data: CreateInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: sprawdzić uprawnienia (owner/admin), wygenerować token zaproszenia
    return InviteResponse(token="mock-invite-token", invite_url=None)


@router.post("/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_organization(
    data: JoinByInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: sprawdzić token, dodać usera do organizacji
    return Response(status_code=204)
