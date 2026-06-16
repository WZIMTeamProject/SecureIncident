from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateInviteRequest(BaseModel):
    role_id: UUID
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = None


class JoinByInviteRequest(BaseModel):
    token: str
