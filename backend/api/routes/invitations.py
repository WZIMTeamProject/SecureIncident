from fastapi import APIRouter, status
 
from api.schemas.invitation.request import CreateInviteRequest, JoinByInviteRequest
from api.schemas.invitation.response import InviteResponse, InvitePreviewResponse
from api.schemas.common.enums import InviteScope
 
router = APIRouter(tags=["Invitations"])
 
@router.post("/projects/{project_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def create_project_invite(project_id: str, body: CreateInviteRequest):
    # TODO: utwórz token zaproszenia do projektu
    return InviteResponse(token="dummy-invite-token", inviteUrl=None)
 
 
@router.post("/projects/join", status_code=status.HTTP_204_NO_CONTENT)
def join_project(body: JoinByInviteRequest):
    # TODO: do³¹cz zalogowanego u¿ytkownika do projektu na podstawie tokenu
    return
 
@router.get("/invites/{token}", response_model=InvitePreviewResponse)
def get_invite_preview(token: str):
    # TODO: pobierz podgl¹d zaproszenia przed akceptacj¹
    return InvitePreviewResponse(
        scope=InviteScope.PROJECT,
        targetName="Test Project",
        isValid=True,
        expiresAt=None,
    )
 