from pydantic import BaseModel, ConfigDict, Field
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
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50)
    permissions: RolePermissions


class UpdateRoleRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    permissions: Optional[RolePermissions] = None
