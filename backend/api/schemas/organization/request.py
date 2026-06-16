from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None


class CreateInviteRequest(BaseModel):
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None


class JoinByInviteRequest(BaseModel):
    token: str
