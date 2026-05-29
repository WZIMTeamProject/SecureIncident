from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import hash_password, hash_token
from db.models.user import User
from db.models.password_reset_token import PasswordResetToken

class UserRepository:
    """Repozytorium dla User i PasswordResetToken."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
    """Pobierz u¿ytkownika po ID."""
    stmt = select(User).where(User.id == user_id)
    return await self.db.scalar_one_or_none(stmt)

async def get_user_by_username(self, username: str) -> Optional[User]:
    """Pobierz u¿ytkownika po username."""
    stmt = select(User).where(User.username == username)
    return await self.db.scalar_one_or_none(stmt)

async def get_user_by_email(self, email: str) -> Optional[User]:
    """Pobierz u¿ytkownika po email."""
    stmt = select(User).where(User.email == email)
    return await self.db.scalar_one_or_none(stmt)

async def get_user_by_email_or_username(self, email_or_username: str) -> Optional[User]:
    """Pobierz u¿ytkownika po email lub username."""
    stmt = select(User).where(
        (User.email == email_or_username) | (User.username == email_or_username)
    )
    return await self.db.scalar_one_or_none(stmt)

async def create_user(
    self,
    first_name: str,
    last_name: str,
    username: str,
    email: str,
    password: str,
    organization_id: Optional[UUID] = None,
) -> User:
    """Utwórz nowego u¿ytkownika."""
    hashed_password = hash_password(password)
    
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=hashed_password,
        organization_id=organization_id,
        is_active=True,
    )
    
    self.db.add(user)
    await self.db.commit()
    await self.db.refresh(user)
    return user

async def user_exists(self, username: str, email: str) -> bool:
    """SprawdŸ czy u¿ytkownik ju¿ istnieje (username lub email)."""
    stmt = select(User).where(
        (User.username == username) | (User.email == email)
    )
    result = await self.db.scalar_one_or_none(stmt)
    return result is not None

async def create_password_reset_token(
    self,
    user_id: UUID,
    raw_token: str,
    expire_minutes: int = 30,
) -> PasswordResetToken:
    """Utwórz token resetowania has³a (zapisz hasz tokenu)."""
    hashed_token = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    
    token_record = PasswordResetToken(
        user_id=user_id,
        token=hashed_token,
        expires_at=expires_at,
    )
    
    self.db.add(token_record)
    await self.db.commit()
    await self.db.refresh(token_record)
    return token_record

async def get_valid_password_reset_token(
    self,
    raw_token: str,
) -> Optional[tuple[PasswordResetToken, User]]:
    """Pobierz wa¿ny token resetowania has³a."""
    hashed_token = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    
    stmt = select(PasswordResetToken).where(
        and_(
            PasswordResetToken.token == hashed_token,
            PasswordResetToken.expires_at > now,
            PasswordResetToken.used_at.is_(None),
        )
    )
    
    token_record = await self.db.scalar_one_or_none(stmt)
    if not token_record:
        return None
    
    user = token_record.user
    return (token_record, user)

async def mark_token_as_used(self, token_record: PasswordResetToken) -> None:
    """Oznacz token resetowania has³a jako u¿yty."""
    token_record.used_at = datetime.now(timezone.utc)
    await self.db.commit()
    await self.db.refresh(token_record)

async def update_password(self, user: User, new_password: str) -> None:
    """Zaktualizuj has³o u¿ytkownika."""
    user.password = hash_password(new_password)
    await self.db.commit()
    await self.db.refresh(user)