from uuid import UUID

from pydantic import BaseModel


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None


class InviteResponse(BaseModel):
    token: str
    invite_url: str | None = None
