from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from core.security import validate_password_strength


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=72)
    remember_user: bool = False


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email_or_username: str = Field(min_length=1, max_length=100)


class PasswordResetConfirmRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reset_token: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)