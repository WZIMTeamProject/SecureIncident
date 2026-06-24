from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectScope(StrEnum):
    PRIVATE = "PRIVATE"
    ORGANIZATION = "ORGANIZATION"


class CreateProjectRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)
    scope: ProjectScope


class UpdateProjectRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)


class AddProjectMemberRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class AssignRoleRequest(BaseModel):
    role_id: UUID
