from fastapi import APIRouter, Response, status
from api.schemas.organization.request import CreateOrganizationRequest
from api.schemas.organization.response import OrganizationResponse
from api.schemas.common.base import CreatedIdResponse
from api.schemas.organization.response import InviteResponse

from api.schemas.organization.request import (
    CreateInviteRequest,
    JoinByInviteRequest
)

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_organization(data: CreateOrganizationRequest):
    # TODO:
    # - stworzyć organizację
    # - przypisać ownera
    
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("", response_model=OrganizationResponse)
def get_current_organization():
    # TODO:
    # - zwrócić organizację użytkownika (jeśli jest przypisany, inaczej 404)
    
    return OrganizationResponse(
        id="00000000-0000-0000-0000-000000000000",
        name="Test Organization",
        description="Test description"
    )




@router.post("/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def create_invite(data: CreateInviteRequest):
    # TODO:
    # - sprawdzić uprawnienia (owner/admin)
    # - wygenerować token zaproszenia

    return InviteResponse(
        token="mock-invite-token",
        inviteUrl=None
    )



@router.post("/join", status_code=status.HTTP_204_NO_CONTENT)
def join_organization(data: JoinByInviteRequest):
    # TODO:
    # - sprawdzić token
    # - dodać usera do organizacji
    
    return Response(status_code=204)