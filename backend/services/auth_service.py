import datetime
import logging
import uuid
from dataclasses import dataclass

from api.schemas.auth.request import LoginRequest, RegisterRequest
from core import security
from core.config import settings
from db import repositories
from db.models.user import User
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services import email_service

logger = logging.getLogger(__name__)


@dataclass
class IssuedTokens:
    """Result of minting/rotating an access + refresh token pair.

    The raw refresh token is returned to the route so it can be written into an
    HttpOnly cookie — it is never persisted or returned in the JSON body.
    """

    access_token: str
    raw_refresh_token: str
    refresh_max_age: int  # cookie Max-Age in seconds
    expires_in: int  # access-token TTL in seconds
    user: User | None = None


def _now_naive() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def _refresh_unauthorized() -> HTTPException:
    # Generic detail — never reveal whether the token was missing, expired or reused.
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    """Register a new user."""
    if await repositories.user_repo.get_user_by_username(db, data.username):
        logger.warning("Registration failed: username already taken")
        raise HTTPException(status_code=409, detail="Username already registered")
    if await repositories.user_repo.get_user_by_email(db, data.email):
        logger.warning("Registration failed: email already registered")
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = security.hash_password(data.password)
    user = await repositories.user_repo.create_user(
        db,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        email=str(data.email),
        password=hashed,
    )
    await db.commit()
    logger.info("User registered user_id=%s", user.id)
    return user


async def login_user(db: AsyncSession, data: LoginRequest) -> IssuedTokens:
    """Authenticate the user and mint a fresh access + refresh token family."""
    user = await repositories.user_repo.get_user_by_username(db, data.username)
    if user is None or not security.verify_password(data.password, user.password):
        logger.warning("Login failed: invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    if not user.is_active:
        logger.warning("Login failed: inactive account user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    family_id = uuid.uuid4()
    access_token = security.create_access_token(str(user.id), family_id)

    # Mirror the password-reset generate -> hash -> store -> commit ordering: the
    # raw token leaves the service (for the cookie); only its hash is persisted.
    raw_refresh_token = security.generate_token()
    refresh_minutes = (
        settings.REFRESH_TOKEN_REMEMBER_EXPIRE_MINUTES
        if data.remember_user
        else settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    expires_at = _now_naive() + datetime.timedelta(minutes=refresh_minutes)
    await repositories.refresh_token_repo.create_refresh_token(
        db,
        token_hash=security.hash_token(raw_refresh_token),
        family_id=family_id,
        user_id=user.id,
        expires_at=expires_at,
    )
    await db.commit()

    logger.info("User logged in user_id=%s", user.id)
    return IssuedTokens(
        access_token=access_token,
        raw_refresh_token=raw_refresh_token,
        refresh_max_age=refresh_minutes * 60,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user,
    )


async def refresh_tokens(db: AsyncSession, raw_refresh_token: str) -> IssuedTokens:
    """Rotate a refresh token: validate, detect reuse, and mint a new pair.

    RFC 9700 Option C: refresh tokens are single-use. Replaying a consumed (or
    family-revoked) token is treated as theft and revokes the entire family.
    """
    token_hash = security.hash_token(raw_refresh_token)
    now_naive = _now_naive()

    row = await repositories.refresh_token_repo.get_by_hash(db, token_hash)
    if row is None or row.expires_at < now_naive:
        logger.warning("Refresh rejected: token unknown or expired")
        raise _refresh_unauthorized()

    if await repositories.revoked_family_repo.is_family_revoked(db, row.family_id):
        logger.warning(
            "Refresh rejected: family already revoked user_id=%s", row.user_id
        )
        raise _refresh_unauthorized()

    # Atomic single-use consumption is the authoritative reuse guard (C-1): a
    # plain read-then-write would let two concurrent replays both pass and never
    # trip detection. A False return means the token was already consumed.
    if not await repositories.refresh_token_repo.mark_used(db, row.id):
        # Reuse detection (I-2): nuke the family and denylist it for as long as any
        # access token in the family could still be alive (ACCESS_TOKEN_EXPIRE_MINUTES).
        logger.warning(
            "Refresh reuse detected: revoking family user_id=%s", row.user_id
        )
        await repositories.refresh_token_repo.revoke_family(db, row.family_id)
        await repositories.revoked_family_repo.add_revoked_family(
            db,
            family_id=row.family_id,
            expires_at=now_naive
            + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        await db.commit()
        raise _refresh_unauthorized()

    access_token = security.create_access_token(str(row.user_id), row.family_id)
    new_raw_refresh_token = security.generate_token()
    # Carry the family's original expiry forward — rotation does not extend the
    # absolute family lifetime, which also preserves remember-me without a flag.
    new_expires_at = row.expires_at
    await repositories.refresh_token_repo.create_refresh_token(
        db,
        token_hash=security.hash_token(new_raw_refresh_token),
        family_id=row.family_id,
        user_id=row.user_id,
        expires_at=new_expires_at,
    )
    await db.commit()

    refresh_max_age = max(0, int((new_expires_at - now_naive).total_seconds()))
    logger.info("Refresh rotated user_id=%s", row.user_id)
    return IssuedTokens(
        access_token=access_token,
        raw_refresh_token=new_raw_refresh_token,
        refresh_max_age=refresh_max_age,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def logout(
    db: AsyncSession,
    *,
    current_user: User,
    family_id: uuid.UUID | None,
    access_jti: str,
    access_exp: datetime.datetime,
) -> None:
    """Revoke the current access token (jti denylist) and its refresh family."""
    await repositories.revoked_token_repo.add_revoked_token(
        db,
        jti=access_jti,
        user_id=current_user.id,
        expires_at=access_exp,
    )
    if family_id is not None:
        # I-2: bound the family denylist entry by the access token's own expiry.
        await repositories.revoked_family_repo.add_revoked_family(
            db,
            family_id=family_id,
            expires_at=access_exp,
        )
    await db.commit()

    # GC the denylists and expired refresh tokens here rather than on the refresh
    # hot path (W-6): logout is low-frequency, so the full-table sweeps cost
    # nothing per-request and expired rows are bounded by their expires_at anyway.
    await repositories.revoked_token_repo.cleanup_expired_revoked_tokens(db)
    await repositories.revoked_family_repo.cleanup_expired(db)
    await repositories.refresh_token_repo.cleanup_expired(db)
    await db.commit()

    logger.info("User logged out user_id=%s", current_user.id)


async def request_password_reset(
    db: AsyncSession, email_or_username: str, background_tasks: BackgroundTasks
) -> None:
    """Generate password reset token (do not reveal whether user exists)."""
    user = await repositories.user_repo.get_user_by_email_or_username(
        db, email_or_username.strip()
    )
    if user is None:
        return  # Silent — do not reveal user existence

    await repositories.user_repo.delete_pending_reset_tokens(db, user.id)
    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)
    expires_at = datetime.datetime.now(datetime.UTC).replace(
        tzinfo=None
    ) + datetime.timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES)
    await repositories.user_repo.create_password_reset_token(
        db, user_id=user.id, token_hash=token_hash, expires_at=expires_at
    )
    await db.commit()
    background_tasks.add_task(email_service.send_reset_email, user.email, raw_token)
    logger.info("Password reset email queued user_id=%s", user.id)


async def reset_password(db: AsyncSession, raw_token: str, new_password: str) -> None:
    """Reset password using a valid reset token."""
    token_hash = security.hash_token(raw_token)
    token_record = await repositories.user_repo.get_valid_password_reset_token(
        db, token_hash
    )
    if token_record is None:
        logger.warning("Password reset failed: invalid or expired token")
        raise HTTPException(
            status_code=400, detail="Invalid or expired password reset token"
        )

    hashed = security.hash_password(new_password)
    await repositories.user_repo.update_user_password(db, token_record.user_id, hashed)
    await repositories.user_repo.mark_password_reset_token_used(db, token_record)
    await db.commit()
    logger.info("Password reset completed user_id=%s", token_record.user_id)


async def change_password(
    db: AsyncSession,
    *,
    current_user: User,
    current_password: str,
    new_password: str,
) -> None:
    """Change the authenticated user's password (verifies the current one)."""
    if not security.verify_password(current_password, current_user.password):
        logger.warning(
            "Password change failed: wrong current password user_id=%s", current_user.id
        )
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if security.verify_password(new_password, current_user.password):
        logger.warning(
            "Password change failed: new password equals current user_id=%s",
            current_user.id,
        )
        raise HTTPException(
            status_code=400,
            detail="New password must be different from the current password",
        )

    hashed = security.hash_password(new_password)
    await repositories.user_repo.update_user_password(db, current_user.id, hashed)
    await db.commit()
    logger.info("Password changed user_id=%s", current_user.id)
