from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from api.schemas.common.enums import IncidentPriority, IncidentStatus
from api.schemas.common.pagination import PaginatedResponse


class IncidentSummary(BaseModel):
    id: UUID
    title: str
    category_id: Optional[UUID] = None
    priority: IncidentPriority
    status: IncidentStatus
    primary_assignee_id: Optional[UUID] = None
    report_date: datetime


IncidentListResponse = PaginatedResponse[IncidentSummary]


class IncidentDetailsResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str
    category_id: Optional[UUID] = None
    priority: IncidentPriority
    status: IncidentStatus
    reporter_id: UUID
    primary_assignee_id: Optional[UUID] = None
    report_date: datetime
