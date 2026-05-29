import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def hash_password(password: str) -> str:
    """Hash hasła za pomocą bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Weryfikuj hasło w stosunku do hasha."""
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

def decode_token(token: str) -> Optional[str]:
    """Dekoduj JWT i zwróć user_id."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def hash_token(token: str) -> str:
    """Hash surowego tokenu SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_secure_token(length: int = 32) -> str:
    """Wygeneruj bezpieczny token URL-safe."""
    return secrets.token_urlsafe(length)