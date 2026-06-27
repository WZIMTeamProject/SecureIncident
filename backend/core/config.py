from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "secret-workflow-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_REMEMBER_EXPIRE_MINUTES: int = 43200
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = "lax"
    REFRESH_COOKIE_NAME: str = "refresh_token"
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30
    INVITE_EXPIRE_MINUTES: int = 60
    INVITE_MAX_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@localhost"
    SMTP_TLS: bool = False
    FRONTEND_URL: str = "http://localhost:5173"
    LOG_FORMAT: str = "text"
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        extra="ignore",
    )


settings = Settings()
