from typing import Optional
import uuid
import datetime

from pydantic import BaseModel

from api.schemas.common.enums import IncidentLogType
from api.schemas.common.pagination import PaginatedResponse


class IncidentLogEntry(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    actor_id: uuid.UUID
    type: IncidentLogType
    comment: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime.datetime


IncidentLogListResponse = PaginatedResponse[IncidentLogEntry]
