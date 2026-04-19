from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from api.schemas.common.enums import IncidentLogType

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