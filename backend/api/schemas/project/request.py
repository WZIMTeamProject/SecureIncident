from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from uuid import UUID
from enum import Enum


class ProjectScope(str, Enum):
    PRIVATE = "PRIVATE"
    ORGANIZATION = "ORGANIZATION"


class CreateProjectRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    scope: ProjectScope


class UpdateProjectRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class AddProjectMemberRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class AssignRoleRequest(BaseModel):
    role_id: UUID
