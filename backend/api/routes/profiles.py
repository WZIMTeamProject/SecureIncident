from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from api.dependencies.db import get_db             # Dostosuj ścieżkę importu get_db, jeśli znajduje się w innym miejscu
from api.dependencies.auth import get_current_user  # Dostosuj ścieżkę importu zależności auth
from api.schemas.profile.request import UpdateProfileRequest
from api.schemas.profile.response import ProfileResponse, UserSearchResponse
from services import profile_service   # Import z katalogu backend/services zgodnie z Twoją strukturę

router = APIRouter(tags=["Profiles"])
users_router = APIRouter(tags=["Users"])


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


@users_router.get("/search", response_model=UserSearchResponse)
async def search_users(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSearchResponse:
    return await profile_service.search_users(db, query, current_user)