from uuid import UUID

from api.schemas.common.pagination import PaginatedResponse
from pydantic import BaseModel

from .request import ProjectScope


class ProjectResponse(BaseModel):
    id: UUID
    organization_id: UUID | None = None
    name: str
    description: str | None = None
    scope: ProjectScope


ProjectListResponse = PaginatedResponse[ProjectResponse]


class ProjectMemberResponse(BaseModel):
    user_id: UUID
    username: str
    role_id: UUID
    role_name: str


class ProjectMemberListResponse(BaseModel):
    members: list[ProjectMemberResponse]
