from uuid import UUID

from api.schemas.common.pagination import PaginatedResponse
from pydantic import BaseModel

from .request import RolePermissions


class RoleResponse(BaseModel):
    id: UUID
    name: str
    permissions: RolePermissions


RoleListResponse = PaginatedResponse[RoleResponse]
