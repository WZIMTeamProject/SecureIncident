from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.schemas.common.enums import InviteScope


class InviteResponse(BaseModel):
    token: str
    invite_url: Optional[str] = None


class InvitePreviewResponse(BaseModel):
    scope: InviteScope
    target_name: str
    is_valid: bool
    expires_at: Optional[datetime] = None
