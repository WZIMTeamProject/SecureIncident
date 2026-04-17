from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from .request import ProjectScope


class ProjectResponse(BaseModel):
    id: UUID
    organizationId: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    scope: ProjectScope


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]


class ProjectMemberResponse(BaseModel):
    userId: UUID
    username: str
    roleId: UUID
    roleName: str


class ProjectMemberListResponse(BaseModel):
    members: List[ProjectMemberResponse]