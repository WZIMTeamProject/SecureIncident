from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from uuid import UUID
from api.schemas.common.enums import IncidentPriority, IncidentStatus


class CreateIncidentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    category_id: Optional[UUID] = None
    priority: Optional[IncidentPriority] = None
    primary_assignee_id: Optional[UUID] = None


class UpdateIncidentStatusRequest(BaseModel):
    status: IncidentStatus

    @field_validator("status")
    @classmethod
    def status_must_not_be_closed(cls, v: IncidentStatus) -> IncidentStatus:
        if v == IncidentStatus.CLOSED:
            raise ValueError("Use the /close endpoint to close an incident")
        return v


class UpdateIncidentAssigneeRequest(BaseModel):
    primary_assignee_id: Optional[UUID] = None


class UpdateIncidentPriorityRequest(BaseModel):
    priority: IncidentPriority


class UpdateIncidentCategoryRequest(BaseModel):
    category_id: UUID


class AddCommentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    content: str = Field(min_length=1, max_length=5000)


class AddHelperRequest(BaseModel):
    user_id: UUID
