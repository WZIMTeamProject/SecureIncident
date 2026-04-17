from pydantic import BaseModel


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