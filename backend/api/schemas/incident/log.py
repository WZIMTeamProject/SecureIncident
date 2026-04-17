from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class IncidentLogType(str, Enum):
    COMMENT = "COMMENT"
    STATUS_CHANGED = "STATUS_CHANGED"
    ASSIGNEE_CHANGED = "ASSIGNEE_CHANGED"


class IncidentLogEntry(BaseModel):
    id: UUID
    type: IncidentLogType
    createdAt: datetime
    actorId: Optional[UUID] = None
    comment: Optional[str] = None
    oldValue: Optional[str] = None
    newValue: Optional[str] = None


class IncidentLogListResponse(BaseModel):
    logs: List[IncidentLogEntry]