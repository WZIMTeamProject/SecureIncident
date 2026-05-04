from pydantic import BaseModel
from typing import Optional

class RolePermissions(BaseModel):
    canWriteTickets: bool
    canHelp: bool
    canAssignHelp: bool
    canMakeRoles: bool
    canChangeRoles: bool
    canAssignPeopleToProject: bool

class CreateRoleRequest(BaseModel):
    name: str
    permissions: RolePermissions

class UpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    permissions: Optional[RolePermissions] = None