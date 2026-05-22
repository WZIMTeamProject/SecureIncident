from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from .request import ProjectScope
from api.schemas.common.pagination import PaginatedResponse


class ProjectResponse(BaseModel):
    id: UUID
    organization_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    scope: ProjectScope


ProjectListResponse = PaginatedResponse[ProjectResponse]


class ProjectMemberResponse(BaseModel):
    user_id: UUID
    username: str
    role_id: UUID
    role_name: str


class ProjectMemberListResponse(BaseModel):
    members: List[ProjectMemberResponse]
