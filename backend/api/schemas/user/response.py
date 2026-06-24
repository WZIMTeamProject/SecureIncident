from uuid import UUID

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: UUID
    username: str
    organization_id: UUID | None = None
