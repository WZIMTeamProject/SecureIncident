import datetime
from uuid import UUID

from api.schemas.profile.request import UpdateProfileRequest
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.password_reset_token import PasswordResetToken
from db.models.user import User
from db.models.user_project import UserProject


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_email_or_username(db: AsyncSession, value: str) -> User | None:
    """Get user by email or username."""
    result = await db.execute(
        select(User).where(or_(User.email == value, User.username == value))
    )
    return result.scalar_one_or_none()


async def get_valid_password_reset_token(db: AsyncSession, token: str):
    now_naive = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

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
    """Create new user (password already hashed)."""
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password=password,
    )
    db.add(user)
    await db.flush()
    return user


async def update_user_password(
    db: AsyncSession, user_id: UUID, hashed_password: str
) -> None:
    """Update user password."""
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
    """Create password reset token (save token hash)."""

    record = PasswordResetToken(
        user_id=user_id,
        token=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    await db.flush()
    return record


async def delete_pending_reset_tokens(db: AsyncSession, user_id: UUID) -> None:
    await db.execute(
        delete(PasswordResetToken).where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at == None,
        )
    )
    await (
        db.flush()
    )  # visible to subsequent queries in same transaction; caller commits


async def mark_password_reset_token_used(
    db: AsyncSession, token: PasswordResetToken
) -> None:
    """Mark password reset token as used."""
    token.used_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

    db.add(token)
    await db.flush()


async def update_user_profile(
    db: AsyncSession,
    user: User,
    data: UpdateProfileRequest,
) -> None:
    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    # No commit here — caller (service) commits


async def search_users_by_username(
    db: AsyncSession,
    query: str,
    organization_id: UUID | None,
    user_id: UUID,
    limit: int = 20,
) -> list[User]:
    # Users in same org OR sharing at least one project with the current user
    shared_project_users = select(UserProject.user_id).where(
        UserProject.project_id.in_(
            select(UserProject.project_id).where(UserProject.user_id == user_id)
        ),
        UserProject.user_id != user_id,
    )

    scope_clauses = [User.id.in_(shared_project_users)]
    if organization_id is not None:
        scope_clauses.append(User.organization_id == organization_id)

    conditions = [
        User.username.ilike(f"%{query}%"),
        User.is_active == True,
        or_(*scope_clauses),
    ]

    stmt = select(User).where(*conditions).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
