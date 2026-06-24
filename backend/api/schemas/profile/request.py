from pydantic import BaseModel, ConfigDict, Field, field_validator


class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str | None = Field(None, min_length=3, max_length=50)
    bio: str | None = Field(None, max_length=1000)
    profile_picture_url: str | None = Field(None, max_length=500)

    @field_validator("profile_picture_url")
    @classmethod
    def validate_picture_url_scheme(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith(("https://", "http://")):
            raise ValueError("profile_picture_url must be an http or https URL")
        return v
