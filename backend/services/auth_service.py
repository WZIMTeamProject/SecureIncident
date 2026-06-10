from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.auth.request import LoginRequest, RegisterRequest
from core import security
from core.config import settings
from db.models.user import User
from db import repositories


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    """Zarejestruj nowego u¿ytkownika."""
    if await repositories.user_repo.get_user_by_username(db, data.username):
        raise HTTPException(status_code=409, detail="Nazwa u¿ytkownika ju¿ zarejestrowana")
    if await repositories.user_repo.get_user_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="Email ju¿ zarejestrowany")

    hashed = security.hash_password(data.password)
    return await repositories.user_repo.create_user(
        db,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        email=str(data.email),
        password=hashed,
    )


async def login_user(db: AsyncSession, data: LoginRequest) -> tuple[User, str]:
    """Uwierzytelnij i zwróæ (user, token)."""
    user = await repositories.user_repo.get_user_by_username(db, data.username)
    if user is None or not security.verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Nieprawid³owe dane uwierzytelniaj¹ce"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Konto jest nieaktywne")

    token = security.create_access_token(str(user.id), remember_user=data.remember_user)
    return user, token


async def request_password_reset(db: AsyncSession, email_or_username: str) -> None:
    """Wygeneruj token resetowania has³a (nie ujawniaj czy user istnieje)."""
    user = await repositories.user_repo.get_user_by_email_or_username(
        db, email_or_username.strip()
    )
    if user is None:
        return  # Silent — do not reveal user existence

    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    await repositories.user_repo.create_password_reset_token(
        db, user_id=user.id, token_hash=token_hash, expires_at=expires_at
    )
    # EMAIL_TODO: send reset email with raw_token


async def reset_password(db: AsyncSession, raw_token: str, new_password: str) -> None:
    """Zresetuj has³o korzystaj¹c z tokenu."""
    token_hash = security.hash_token(raw_token)
    token_record = await repositories.user_repo.get_valid_password_reset_token(db, token_hash)
    if token_record is None:
        raise HTTPException(status_code=400, detail="Nieprawid³owy lub wygas³y token resetowania has³a")

    hashed = security.hash_password(new_password)
    await repositories.user_repo.update_user_password(db, token_record.user_id, hashed)
    await repositories.user_repo.mark_password_reset_token_used(db, token_record)
    await db.commit()