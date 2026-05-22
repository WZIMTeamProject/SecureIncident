from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_user: bool = False


class PasswordResetRequest(BaseModel):
    email_or_username: str


class PasswordResetConfirmRequest(BaseModel):
    reset_token: str
    new_password: str
