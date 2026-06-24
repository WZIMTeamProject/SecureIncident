from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateOrganizationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None, max_length=2000)


class CreateInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    expires_at: datetime | None = None
    max_uses: int | None = Field(None, gt=0)


class JoinByInviteRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    token: str = Field(min_length=1, max_length=255)
