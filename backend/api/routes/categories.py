from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.common.base import CreatedIdResponse
from api.schemas.category.response import (
    CategoryResponse,
    CategoryListResponse,
)
from api.schemas.category.request import (
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from db.models.user import User


router = APIRouter(prefix="/projects/{project_id}/categories", tags=["Categories"])


@router.get("", response_model=CategoryListResponse)
async def get_categories(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: logika pobierania kategorii
    return CategoryListResponse(items=[], total=0, offset=0, limit=20)


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    project_id: UUID,
    body: CreateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: logika tworzenia kategorii
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.patch("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_category(
    project_id: UUID,
    category_id: UUID,
    body: UpdateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: logika aktualizowania kategorii
    return


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    project_id: UUID,
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: logika usuwania kategorii
    return
