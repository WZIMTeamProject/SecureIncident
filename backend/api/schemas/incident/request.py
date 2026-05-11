from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from api.schemas.common.enums import IncidentPriority, IncidentStatus


class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    category_id: Optional[UUID] = None
    priority: Optional[IncidentPriority] = None
    primary_assignee_id: Optional[UUID] = None


class UpdateIncidentStatusRequest(BaseModel):
    status: IncidentStatus


class UpdateIncidentAssigneeRequest(BaseModel):
    primary_assignee_id: Optional[UUID] = None


class UpdateIncidentPriorityRequest(BaseModel):
    priority: IncidentPriority


class UpdateIncidentCategoryRequest(BaseModel):
    category_id: Optional[UUID] = None


class AddCommentRequest(BaseModel):
    content: str


class AddHelperRequest(BaseModel):
    user_id: UUID
