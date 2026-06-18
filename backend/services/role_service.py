import logging
from uuid import UUID
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.role.request import CreateRoleRequest, UpdateRoleRequest
from db.models.project import Project
from db.models.role import Role
from db.models.user import User
from db import repositories

logger = logging.getLogger(__name__)


async def list_roles(
    db: AsyncSession,
    *,
    project_id: UUID,
    current_user: User,
) -> Sequence[Role]:
    """List project roles (requires project membership)."""
    await _require_member(db, project_id, current_user)
    return await repositories.project_repo.list_roles_for_project(db, project_id)


async def get_role(
    db: AsyncSession,
    *,
    project_id: UUID,
    role_id: UUID,
    current_user: User,
) -> Role:
    """Role details (requires project membership)."""
    await _require_member(db, project_id, current_user)

    role = await repositories.project_repo.get_role_by_id(db, role_id)
    if role is None or role.project_id != project_id:
        logger.warning(
            "Role fetch failed: role not found role_id=%s project_id=%s user_id=%s",
            role_id,
            project_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found in this project",
        )
    return role


async def create_role(
    db: AsyncSession,
    *,
    project_id: UUID,
    data: CreateRoleRequest,
    current_user: User,
) -> Role:
    """Create role in project (project owner only)."""
    await _require_owner(db, project_id, current_user)

    role = await repositories.project_repo.create_role(
        db,
        project_id=project_id,
        name=data.name.strip(),
        permissions=data.permissions.model_dump(),
    )
    await db.commit()
    await db.refresh(role)
    logger.info(
        "Role created role_id=%s project_id=%s user_id=%s",
        role.id,
        project_id,
        current_user.id,
    )
    return role


async def update_role(
    db: AsyncSession,
    *,
    project_id: UUID,
    role_id: UUID,
    data: UpdateRoleRequest,
    current_user: User,
) -> None:
    """Update role name and/or permissions (project owner only)."""
    await _require_owner(db, project_id, current_user)

    role = await repositories.project_repo.get_role_by_id(db, role_id)
    if role is None or role.project_id != project_id:
        logger.warning(
            "Role update failed: role not found role_id=%s project_id=%s user_id=%s",
            role_id,
            project_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found in this project",
        )

    name = data.name.strip() if data.name is not None else None
    permissions = data.permissions.model_dump() if data.permissions is not None else None

    await repositories.project_repo.update_role(
        db, role=role, name=name, permissions=permissions
    )
    await db.commit()
    logger.info(
        "Role updated role_id=%s project_id=%s user_id=%s",
        role_id,
        project_id,
        current_user.id,
    )


# --- authorization helpers (MVP: owner-check / member-check) ---

async def _get_project(db: AsyncSession, project_id: UUID) -> Project:
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        logger.warning("Role operation failed: project not found project_id=%s", project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


async def _require_member(
    db: AsyncSession, project_id: UUID, current_user: User
) -> Project:
    project = await _get_project(db, project_id)
    membership = await repositories.project_repo.get_user_project(
        db, current_user.id, project_id
    )
    if membership is None:
        logger.warning(
            "Role access denied: user not member project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return project


async def _require_owner(
    db: AsyncSession, project_id: UUID, current_user: User
) -> Project:
    project = await _get_project(db, project_id)
    if project.project_owner_id != current_user.id:
        logger.warning(
            "Role management denied: user not owner project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can manage roles",
        )
    return project