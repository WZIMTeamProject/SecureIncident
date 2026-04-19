from pydantic import BaseModel
from typing import Optional

class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None
    profilePictureUrl: Optional[str] = None