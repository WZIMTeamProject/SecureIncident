from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.category import Category


async def get_by_id(db: AsyncSession, category_id: UUID) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_by_project(db: AsyncSession, project_id: UUID) -> Sequence[Category]:
    result = await db.execute(
        select(Category)
        .where(Category.project_id == project_id)
        .order_by(Category.name.asc())
    )
    return result.scalars().all()


async def create(db: AsyncSession, category: Category) -> None:
    db.add(category)
    await db.flush()


async def update(db: AsyncSession, category: Category) -> None:
    db.add(category)
    await db.flush()


async def delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.flush()
