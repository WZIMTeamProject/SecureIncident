from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.project import Project
from db.models.role import Role
from db.models.user import User
from db.models.user_project import UserProject


async def get_project_by_id(db: AsyncSession, project_id: UUID) -> Optional[Project]:
    """Get project by ID."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def get_role_by_id(db: AsyncSession, role_id: UUID) -> Optional[Role]:
    """Get role by ID."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    return result.scalar_one_or_none()


async def create_project(
    db: AsyncSession,
    *,
    name: str,
    description: Optional[str],
    scope: str,
    owner_id: UUID,
    organization_id: Optional[UUID],
) -> Project:
    """Create project (flush only — commit in service)."""
    project = Project(
        name=name,
        description=description,
        scope=scope,
        project_owner_id=owner_id,
        organization_id=organization_id,
    )
    db.add(project)
    await db.flush()
    return project


async def create_role(
    db: AsyncSession,
    *,
    project_id: UUID,
    name: str,
    permissions: dict,
) -> Role:
    """Create role in project (flush only — commit in service).

    `permissions` is a dict with 7 can_* flags (e.g., from RolePermissions.model_dump()).
    """
    role = Role(project_id=project_id, name=name, **permissions)
    db.add(role)
    await db.flush()
    return role


async def get_user_project(
    db: AsyncSession, user_id: UUID, project_id: UUID
) -> Optional[UserProject]:
    """Get user project membership (or None)."""
    result = await db.execute(
        select(UserProject).where(
            UserProject.user_id == user_id,
            UserProject.project_id == project_id,
        )
    )
    return result.scalar_one_or_none()


async def create_user_project(
    db: AsyncSession,
    *,
    user_id: UUID,
    project_id: UUID,
    role_id: UUID,
) -> UserProject:
    """Create user project membership (flush only — commit in service)."""
    membership = UserProject(
        user_id=user_id,
        project_id=project_id,
        role_id=role_id,
    )
    db.add(membership)
    await db.flush()
    return membership


async def list_projects_for_user(
    db: AsyncSession,
    *,
    user_id: UUID,
    scope: Optional[str] = None,
) -> Sequence[Project]:
    """List projects the user is a member of (optional scope filter)."""
    stmt = (
        select(Project)
        .join(UserProject, UserProject.project_id == Project.id)
        .where(UserProject.user_id == user_id)
    )
    if scope is not None:
        stmt = stmt.where(Project.scope == scope)
    result = await db.execute(stmt)
    return result.scalars().all()


async def list_members(
    db: AsyncSession, project_id: UUID
) -> Sequence[tuple[User, Role]]:
    """List (User, Role) pairs for all project members."""
    result = await db.execute(
        select(User, Role)
        .join(UserProject, UserProject.user_id == User.id)
        .join(Role, Role.id == UserProject.role_id)
        .where(UserProject.project_id == project_id)
    )
    return result.all()


async def update_user_project_role(
    db: AsyncSession,
    *,
    membership: UserProject,
    role_id: UUID,
) -> None:
    """Update an existing membership's role (flush only — caller commits)."""
    membership.role_id = role_id
    db.add(membership)
    await db.flush()


async def list_roles_for_project(
    db: AsyncSession, project_id: UUID
) -> Sequence[Role]:
    """List all roles defined in the project."""
    result = await db.execute(
        select(Role).where(Role.project_id == project_id)
    )
    return result.scalars().all()


async def update_role(
    db: AsyncSession,
    *,
    role: Role,
    name: Optional[str] = None,
    permissions: Optional[dict] = None,
) -> None:
    """Update a role's name and/or permissions (flush only — caller commits)."""
    if name is not None:
        role.name = name
    if permissions is not None:
        for flag, value in permissions.items():
            setattr(role, flag, value)
    db.add(role)
    await db.flush()