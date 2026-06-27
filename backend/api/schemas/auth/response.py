from uuid import UUID

from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    id: UUID
    username: str
    organization_id: UUID | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: CurrentUserResponse


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
