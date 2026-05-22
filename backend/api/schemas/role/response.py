from pydantic import BaseModel
from uuid import UUID
from .request import RolePermissions
from api.schemas.common.pagination import PaginatedResponse


class RoleResponse(BaseModel):
    id: UUID
    name: str
    permissions: RolePermissions


RoleListResponse = PaginatedResponse[RoleResponse]
