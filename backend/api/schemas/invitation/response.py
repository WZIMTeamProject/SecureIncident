from datetime import datetime

from api.schemas.common.enums import InviteScope
from pydantic import BaseModel


class InviteResponse(BaseModel):
    token: str
    invite_url: str | None = None


class InvitePreviewResponse(BaseModel):
    scope: InviteScope
    target_name: str
    is_valid: bool
    expires_at: datetime | None = None
