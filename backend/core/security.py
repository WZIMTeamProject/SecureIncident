import hashlib
import secrets
import uuid  # Dodane do generowania JTI
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
import bcrypt
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM


def hash_password(password: str) -> str:
    """Hash hasła za pomocą bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Weryfikuj hasło w stosunku do hasha."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(user_id: str, remember_user: bool = False) -> str:
    """Utwórz JWT token."""
    if remember_user:
        expire_minutes = settings.REMEMBER_ME_EXPIRE_MINUTES
    else:
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid.uuid4()),  # Zmiana: Dodane unikalne ID tokenu
    }

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Dekoduj JWT i zwróć pełny payload (dict). Zgłasza wyjątek na nieudane dekodowanie."""
    # Zmiana: Wymuszamy obecność exp, sub oraz jti w tokenie
    return jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub", "jti"]}
    )


def hash_token(token: str) -> str:
    """Hash surowego tokenu SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token() -> str:
    """Wygeneruj bezpieczny token URL-safe."""
    return secrets.token_urlsafe(32)


def validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(v.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 bytes")
    if not any(c.isupper() for c in v):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in v):
        raise ValueError("Password must contain at least one digit")
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/~`\'"\\' for c in v):
        raise ValueError("Password must contain at least one special character")
    return v