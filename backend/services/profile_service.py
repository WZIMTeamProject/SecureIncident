import logging

from api.schemas.profile.request import UpdateProfileRequest
from api.schemas.profile.response import (
    ProfileResponse,
    UserSearchResponse,
    UserSearchResult,
)
from db.models.user import User
from db.repositories import user_repo
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def get_profile(current_user: User) -> ProfileResponse:
    """Return the authenticated user's profile."""
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        bio=current_user.bio,
        profile_picture_url=current_user.profile_picture_url,
    )


async def update_profile(
    db: AsyncSession,
    current_user: User,
    data: UpdateProfileRequest,
) -> None:
    """Update user profile with username uniqueness validation."""
    if data.username and data.username != current_user.username:
        existing = await user_repo.get_user_by_username(db, data.username)
        if existing:
            logger.warning(
                "Profile update failed: username already taken user_id=%s",
                current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
    await user_repo.update_user_profile(db, current_user, data)
    await db.commit()
    await db.refresh(current_user)
    logger.info("Profile updated user_id=%s", current_user.id)


async def search_users(
    db: AsyncSession,
    query: str,
    current_user: User,
) -> UserSearchResponse:
    """Search for users in the same organization or projects."""
    users = await user_repo.search_users_by_username(
        db=db,
        query=query,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
    )
    return UserSearchResponse(
        users=[UserSearchResult(id=u.id, username=u.username) for u in users]
    )
