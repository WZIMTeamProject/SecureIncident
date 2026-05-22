from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None


class InviteResponse(BaseModel):
    token: str
    invite_url: Optional[str] = None
