from fastapi import APIRouter, status
from uuid import UUID
 
from api.schemas.role.request import CreateRoleRequest
from api.schemas.role.response import RoleListResponse, CreatedIdResponse
 
router = APIRouter(prefix="/projects/{project_id}/roles", tags=["Roles"])
 
 
@router.get("", response_model=RoleListResponse)
def get_roles(project_id: UUID):
    # TODO: pobierz role z bazy dla danego projektu
    roles = [] 
    return RoleListResponse(roles=roles)
 
 
@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_role(project_id: UUID, body: CreateRoleRequest):
    # TODO: utworz role w bazie
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")