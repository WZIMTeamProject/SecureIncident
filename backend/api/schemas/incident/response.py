from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from api.schemas.common.enums import IncidentPriority, IncidentStatus


class IncidentSummary(BaseModel):
    id: UUID
    title: str
    categoryId: UUID
    priority: IncidentPriority
    status: IncidentStatus
    primaryAssigneeId: Optional[UUID] = None
    reportDate: datetime


class IncidentListResponse(BaseModel):
    incidents: List[IncidentSummary]


class IncidentDetailsResponse(BaseModel):
    id: UUID
    projectId: UUID
    title: str
    description: str
    categoryId: UUID
    priority: IncidentPriority
    status: IncidentStatus
    reporterId: UUID
    primaryAssigneeId: Optional[UUID] = None
    reportDate: datetime