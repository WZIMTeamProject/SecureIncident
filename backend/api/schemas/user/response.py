from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class UserResponse(BaseModel):
    id: UUID
    username: str
    organizationId: Optional[UUID] = None