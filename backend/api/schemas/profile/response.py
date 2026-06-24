from uuid import UUID

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: UUID
    username: str
    bio: str | None = None
    profile_picture_url: str | None = None


class UserSearchResult(BaseModel):
    id: UUID
    username: str


class UserSearchResponse(BaseModel):
    users: list[UserSearchResult]
