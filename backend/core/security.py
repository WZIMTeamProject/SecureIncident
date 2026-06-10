import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM


def hash_password(password: str) -> str:
    """Hash has³a za pomoc¹ bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Weryfikuj has³o w stosunku do hasha."""
    return pwd_context.verify(plain_password, hashed_password)


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
    }

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Dekoduj JWT i zwróæ pe³ny payload (dict). Zg³asza wyj¹tek na nieudane dekodowanie."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def hash_token(token: str) -> str:
    """Hash surowego tokenu SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token() -> str:
    """Wygeneruj bezpieczny token URL-safe."""
    return secrets.token_urlsafe(32)