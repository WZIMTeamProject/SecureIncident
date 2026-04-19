from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.schemas.common.enums import InviteScope

class InviteResponse(BaseModel):
    token: str
    inviteUrl: Optional[str] = None

class InvitePreviewResponse(BaseModel):
    scope: InviteScope  
    targetName: str
    isValid: bool
    expiresAt: Optional[datetime] = None