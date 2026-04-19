from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateInviteRequest(BaseModel):
    expiresAt: Optional[datetime] = None
    maxUses: Optional[int] = None

class JoinByInviteRequest(BaseModel):
    token: str