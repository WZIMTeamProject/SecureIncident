import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.category.request import CreateCategoryRequest, UpdateCategoryRequest
from api.schemas.category.response import CategoryListResponse, CategoryResponse
from api.schemas.common.base import CreatedIdResponse
from db import repositories
from db.models.category import Category
from db.models.user import User
from db.models.user_project import UserProject

logger = logging.getLogger(__name__)


async def _get_membership_or_403(db: AsyncSession, project_id: UUID, user_id: UUID) -> UserProject:
    m = await repositories.project_repo.get_user_project(db, user_id, project_id)
    if m is None:
        logger.warning(
            "Category access denied: user not project member project_id=%s user_id=%s",
            project_id,
            user_id,
        )
        raise HTTPException(status_code=403, detail="Not a project member")
    return m


async def list_categories(
    db: AsyncSession,
    project_id: UUID,
    current_user: User,
) -> CategoryListResponse:
    await _get_membership_or_403(db, project_id, current_user.id)
    categories = await repositories.category_repo.get_by_project(db, project_id)
    items = [CategoryResponse(id=c.id, name=c.name, description=c.description) for c in categories]
    return CategoryListResponse(items=items, total=len(items), limit=len(items), offset=0)


async def create_category(
    db: AsyncSession,
    project_id: UUID,
    data: CreateCategoryRequest,
    current_user: User,
) -> CreatedIdResponse:
    membership = await _get_membership_or_403(db, project_id, current_user.id)
    if not getattr(membership.role, "can_make_roles", False):
        logger.warning(
            "Category create failed: insufficient permissions project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    category = Category(project_id=project_id, name=data.name, description=data.description)
    await repositories.category_repo.create(db, category)
    await db.commit()
    await db.refresh(category)
    logger.info("Category created category_id=%s project_id=%s user_id=%s", category.id, project_id, current_user.id)
    return CreatedIdResponse(id=category.id)


async def update_category(
    db: AsyncSession,
    project_id: UUID,
    category_id: UUID,
    data: UpdateCategoryRequest,
    current_user: User,
) -> None:
    membership = await _get_membership_or_403(db, project_id, current_user.id)
    if not getattr(membership.role, "can_make_roles", False):
        logger.warning(
            "Category update failed: insufficient permissions category_id=%s project_id=%s user_id=%s",
            category_id,
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    category = await repositories.category_repo.get_by_id(db, category_id)
    if category is None or category.project_id != project_id:
        logger.warning(
            "Category update failed: not found category_id=%s project_id=%s user_id=%s",
            category_id,
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="Category not found in this project")

    if data.name is not None:
        category.name = data.name
    await repositories.category_repo.update(db, category)
    await db.commit()
    logger.info("Category updated category_id=%s project_id=%s user_id=%s", category_id, project_id, current_user.id)


async def delete_category(
    db: AsyncSession,
    project_id: UUID,
    category_id: UUID,
    current_user: User,
) -> None:
    membership = await _get_membership_or_403(db, project_id, current_user.id)
    if not getattr(membership.role, "can_make_roles", False):
        logger.warning(
            "Category delete failed: insufficient permissions category_id=%s project_id=%s user_id=%s",
            category_id,
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    category = await repositories.category_repo.get_by_id(db, category_id)
    if category is None or category.project_id != project_id:
        logger.warning(
            "Category delete failed: not found category_id=%s project_id=%s user_id=%s",
            category_id,
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="Category not found in this project")

    await repositories.category_repo.delete(db, category)
    await db.commit()
    logger.info("Category deleted category_id=%s project_id=%s user_id=%s", category_id, project_id, current_user.id)
