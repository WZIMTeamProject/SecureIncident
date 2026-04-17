from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str
    rememberUser: bool = False


class PasswordResetRequest(BaseModel):
    emailOrUsername: str


class PasswordResetConfirmRequest(BaseModel):
    resetToken: str
    newPassword: str