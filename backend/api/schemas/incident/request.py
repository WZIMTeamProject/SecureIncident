from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from api.schemas.common.enums import IncidentPriority, IncidentStatus


class CreateIncidentRequest(BaseModel):
    title: str
    description: str
    categoryId: UUID
    priority: Optional[IncidentPriority] = None
    primaryAssigneeId: Optional[UUID] = None


class UpdateIncidentStatusRequest(BaseModel):
    status: IncidentStatus


class UpdateIncidentAssigneeRequest(BaseModel):
    primaryAssigneeId: Optional[UUID] = None


class UpdateIncidentPriorityRequest(BaseModel):
    priority: IncidentPriority


class UpdateIncidentCategoryRequest(BaseModel):
    categoryId: UUID


class AddCommentRequest(BaseModel):
    content: str

class AddHelperRequest(BaseModel):
    userId: UUID