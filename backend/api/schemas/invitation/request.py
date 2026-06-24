from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    role_id: UUID
    expires_at: datetime | None = None
    max_uses: int | None = Field(None, gt=0)


class JoinByInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(min_length=1, max_length=255)
