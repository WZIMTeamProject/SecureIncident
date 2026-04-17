from pydantic import BaseModel
from typing import List
from uuid import UUID
from .request import RolePermissions


class RoleResponse(BaseModel):
    id: UUID
    name: str
    permissions: RolePermissions


class RoleListResponse(BaseModel):
    roles: List[RoleResponse]