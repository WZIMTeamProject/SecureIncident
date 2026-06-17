from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class CreateInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    role_id: UUID
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, gt=0)


class JoinByInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(min_length=1, max_length=255)
