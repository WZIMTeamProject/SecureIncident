from datetime import datetime
from uuid import UUID

from api.schemas.common.enums import IncidentPriority, IncidentStatus
from api.schemas.common.pagination import PaginatedResponse
from pydantic import BaseModel


class IncidentSummary(BaseModel):
    id: UUID
    title: str
    category_id: UUID | None = None
    priority: IncidentPriority
    status: IncidentStatus
    primary_assignee_id: UUID | None = None
    report_date: datetime


IncidentListResponse = PaginatedResponse[IncidentSummary]


class HelperResponse(BaseModel):
    user_id: UUID
    added_at: datetime


class IncidentDetailsResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str
    category_id: UUID | None = None
    priority: IncidentPriority
    status: IncidentStatus
    reporter_id: UUID
    primary_assignee_id: UUID | None = None
    report_date: datetime
    closing_date: datetime | None = None
    helpers: list[HelperResponse] = []
