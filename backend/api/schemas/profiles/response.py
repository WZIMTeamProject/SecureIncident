from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class ProfileResponse(BaseModel):
    id: UUID
    username: str
    bio: Optional[str] = None
    profilePictureUrl: Optional[str] = None

class UserSearchResult(BaseModel):
    id: UUID
    username: str

class UserSearchResponse(BaseModel):
    users: List[UserSearchResult]