from datetime import datetime, timezone
import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import select, or_, delete
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

async def get_valid_password_reset_token(db: AsyncSession, token: str):
    now_naive = datetime.datetime.now(timezone.utc).replace(tzinfo=None)
    
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used_at == None,
            PasswordResetToken.expires_at > now_naive,
        )
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
    expires_at: datetime.datetime,
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


async def delete_pending_reset_tokens(db: AsyncSession, user_id: UUID) -> None:
    await db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at == None,
        )
    )
    await db.flush()  # visible to subsequent queries in same transaction; caller commits


async def mark_password_reset_token_used(
    db: AsyncSession, token: PasswordResetToken
) -> None:
    """Oznacz token resetowania hasła jako użyty."""
    token.used_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    
    db.add(token)
    await db.commit()

