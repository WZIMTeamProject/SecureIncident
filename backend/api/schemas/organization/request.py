from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class CreateOrganizationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class CreateInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, gt=0)


class JoinByInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(min_length=1, max_length=255)
