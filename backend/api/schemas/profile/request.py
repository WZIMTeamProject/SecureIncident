from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=1000)
    profile_picture_url: Optional[str] = Field(None, max_length=500)

    @field_validator("profile_picture_url")
    @classmethod
    def validate_picture_url_scheme(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.startswith(("https://", "http://")):
            raise ValueError("profile_picture_url must be an http or https URL")
        return v
