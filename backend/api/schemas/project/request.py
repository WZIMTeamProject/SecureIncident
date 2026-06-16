from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from enum import Enum


class ProjectScope(str, Enum):
    PRIVATE = "PRIVATE"
    ORGANIZATION = "ORGANIZATION"


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None
    scope: ProjectScope


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AddProjectMemberRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class AssignRoleRequest(BaseModel):
    role_id: UUID
