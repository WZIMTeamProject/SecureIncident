from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CurrentUserResponse(BaseModel):
    id: UUID
    username: str
    organization_id: Optional[UUID] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserResponse