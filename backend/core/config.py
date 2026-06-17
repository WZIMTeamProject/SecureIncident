from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ""
    SECRET_KEY: str = "prod_test"
    ALGORITHM: str = "HS256"
    REMEMBER_ME_EXPIRE_MINUTES: int = 10080
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    SMTP_HOST: str = "mailpit"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@localhost"
    SMTP_TLS: bool = False
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent.parent / ".env"
)

settings = Settings()
