from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateOrganizationRequest(BaseModel):
    name: str
    description: Optional[str] = None


class CreateInviteRequest(BaseModel):
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None


class JoinByInviteRequest(BaseModel):
    token: str
