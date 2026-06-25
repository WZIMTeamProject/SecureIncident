from db.models.user import User
from fastapi import APIRouter, Depends, Query
from services import profile_service
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.schemas.profile.response import UserSearchResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSearchResponse:
    return await profile_service.search_users(db, query, current_user)
