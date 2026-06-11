from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, hash_token
from db.models.user import User
from db.models.password_reset_token import PasswordResetToken


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Pobierz użytkownika po ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Pobierz użytkownika po username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Pobierz użytkownika po email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_email_or_username(db: AsyncSession, value: str) -> Optional[User]:
    """Pobierz użytkownika po email lub username."""
    result = await db.execute(
        select(User).where(or_(User.email == value, User.username == value))
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    first_name: str,
    last_name: str,
    username: str,
    email: str,
    password: str,
) -> User:
    """Utwórz nowego użytkownika (hasło już zahashowane)."""
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_password(db: AsyncSession, user_id: UUID, hashed_password: str) -> None:
    """Zaktualizuj hasło użytkownika."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.password = hashed_password


async def create_password_reset_token(
    db: AsyncSession,
    *,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
) -> PasswordResetToken:
    """Utwórz token resetowania hasła (zapisz hasz tokenu)."""
    record = PasswordResetToken(
        user_id=user_id,
        token=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_valid_password_reset_token(
    db: AsyncSession, token_hash: str
) -> Optional[PasswordResetToken]:
    """Pobierz ważny (nie wygasły, nie użyty) token resetowania hasła."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token_hash,
            PasswordResetToken.used_at == None,
            PasswordResetToken.expires_at > now,
        )
    )
    return result.scalar_one_or_none()


async def mark_password_reset_token_used(
    db: AsyncSession, token: PasswordResetToken
) -> None:
    """Oznacz token resetowania hasła jako użyty."""
    token.used_at = datetime.now(timezone.utc)