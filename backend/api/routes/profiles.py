from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.profile.request import UpdateProfileRequest
from api.schemas.profile.response import (
    ProfileResponse,
    UserSearchResponse,
    UserSearchResult,
)
from db.models.user import User


router = APIRouter(tags=["Profiles"])


@router.get("/profiles/me", response_model=ProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProfileResponse(
        id="00000000-0000-0000-0000-000000000000",
        username="test_user",
        bio=None,
        profile_picture_url=None,
    )


@router.patch("/profiles/me", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_profile(
    body: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.get("/users/search", response_model=UserSearchResponse)
async def search_users(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserSearchResponse(users=[
        UserSearchResult(
            id="00000000-0000-0000-0000-000000000000",
            username="test_user",
        )
    ])
