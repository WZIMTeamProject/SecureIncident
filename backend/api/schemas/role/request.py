from pydantic import BaseModel
from typing import Optional


class RolePermissions(BaseModel):
    can_write_tickets: bool
    can_help: bool
    can_assign_help: bool
    can_change_status: bool
    can_make_roles: bool
    can_change_roles: bool
    can_assign_people_to_project: bool


class CreateRoleRequest(BaseModel):
    name: str
    permissions: RolePermissions


class UpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    permissions: Optional[RolePermissions] = None
