from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.profile.request import UpdateProfileRequest
from api.schemas.profile.response import ProfileResponse
from services import profile_service

router = APIRouter(tags=["Profiles"])


@router.get("/profiles/me", response_model=ProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    return await profile_service.get_profile(current_user)


@router.patch("/profiles/me", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_profile(
    data: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await profile_service.update_profile(db, current_user, data)
