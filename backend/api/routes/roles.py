from fastapi import APIRouter, status
from uuid import UUID
 
from api.schemas.role.request import (
   RolePermissions,
   CreateRoleRequest,
   UpdateRoleRequest
)
from api.schemas.role.response import (
   RoleListResponse, 
   RoleResponse
)
from api.schemas.common.base import CreatedIdResponse


router = APIRouter(prefix="/projects/{project_id}/roles", tags=["Roles"])
 
 
@router.get("", response_model=RoleListResponse)
def get_roles(project_id: UUID):
    # TODO: logika pobierania ról 
    roles = [] 
    return RoleListResponse(roles=roles)
 
 
@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_role(project_id: UUID, body: CreateRoleRequest):
    # TODO: logika utworzenia roli 
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")

@router.get("/{role_id}", response_model=RoleResponse)
def get_role(project_id: UUID, role_id: UUID):
    # TODO: logika pobierania szczegó³ów roli
    return RoleResponse(
        id=role_id,
        name="Test Role",
        permissions=RolePermissions(
            canWriteTickets=True,
            canHelp=False,
            canAssignHelp=False,
            canMakeRoles=False,
            canChangeRoles=False,
            canAssignPeopleToProject=False,
        )
    )
 
 
@router.patch("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_role(project_id: UUID, role_id: UUID, body: UpdateRoleRequest):
    # TODO: logika aktualizacji roli
    return 