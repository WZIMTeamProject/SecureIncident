import datetime
import uuid

from api.schemas.common.enums import IncidentLogType
from api.schemas.common.pagination import PaginatedResponse
from pydantic import BaseModel


class IncidentLogEntry(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    actor_id: uuid.UUID
    type: IncidentLogType
    comment: str | None = None
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime.datetime


IncidentLogListResponse = PaginatedResponse[IncidentLogEntry]
