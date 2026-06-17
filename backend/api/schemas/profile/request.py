from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=1000)
    profile_picture_url: Optional[str] = Field(None, max_length=500)
