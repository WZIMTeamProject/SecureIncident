import logging
from collections.abc import Sequence
from uuid import UUID

from api.schemas.project.request import (
    AddProjectMemberRequest,
    AssignRoleRequest,
    CreateProjectRequest,
    ProjectScope,
    UpdateProjectRequest,
)
from db import repositories
from db.models.project import Project
from db.models.user import User
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# ADR-001: Owner role has all permissions. Seeded atomically with project.
_OWNER_PERMISSIONS = {
    "can_write_tickets": True,
    "can_help": True,
    "can_assign_help": True,
    "can_change_status": True,
    "can_make_roles": True,
    "can_change_roles": True,
    "can_assign_people_to_project": True,
}


async def create_project(
    db: AsyncSession,
    *,
    data: CreateProjectRequest,
    current_user: User,
) -> Project:
    """Create project with atomic seeding of 'Owner' role and owner membership.

    Overarching rule (architecture.md): a user belongs to ONE organization
    OR uses only private projects — not both. This implies:

    - scope=ORGANIZATION  → user MUST belong to organization; project owner
      becomes organization owner (ADR-002), even if created by delegate.
    - scope=PRIVATE       → user MUST NOT belong to organization; project owner
      becomes creator.

    Everything (Project + Role 'Owner' + UserProject) is created in one transaction.
    """
    if data.scope == ProjectScope.ORGANIZATION:
        if current_user.organization_id is None:
            logger.warning(
                "Project creation failed: user not in org for org project user_id=%s",
                current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization members can create organization projects",
            )
        organization = await repositories.organization_repo.get_organization_by_id(
            db, current_user.organization_id
        )
        if organization is None:
            logger.warning(
                "Project creation failed: org not found org_id=%s user_id=%s",
                current_user.organization_id,
                current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        owner_id = organization.org_owner_id  # ADR-002
        organization_id: UUID | None = organization.id
    else:  # ProjectScope.PRIVATE
        if current_user.organization_id is not None:
            logger.warning(
                "Project creation failed: org member attempted private project user_id=%s",
                current_user.id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization members cannot create private projects",
            )
        owner_id = current_user.id
        organization_id = None

    # --- one transaction: project -> Owner role -> owner membership ---
    project = await repositories.project_repo.create_project(
        db,
        name=data.name.strip(),
        description=data.description,
        scope=data.scope.value,
        owner_id=owner_id,
        organization_id=organization_id,
    )

    owner_role = await repositories.project_repo.create_role(
        db,
        project_id=project.id,
        name="Owner",
        permissions=_OWNER_PERMISSIONS,
    )

    await repositories.project_repo.create_user_project(
        db,
        user_id=owner_id,
        project_id=project.id,
        role_id=owner_role.id,
    )

    await db.commit()
    await db.refresh(project)
    logger.info("Project created project_id=%s user_id=%s", project.id, current_user.id)
    return project


async def list_projects(
    db: AsyncSession,
    *,
    current_user: User,
    scope: ProjectScope | None = None,
) -> Sequence[Project]:
    """List projects where current user is a member."""
    return await repositories.project_repo.list_projects_for_user(
        db,
        user_id=current_user.id,
        scope=scope.value if scope is not None else None,
    )


async def get_project(
    db: AsyncSession,
    *,
    project_id: UUID,
    current_user: User,
) -> Project:
    """Get project — only if user is a member."""
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        logger.warning(
            "Project fetch failed: project not found project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="Project not found")

    membership = await repositories.project_repo.get_user_project(
        db, current_user.id, project_id
    )
    if membership is None:
        logger.warning(
            "Project access denied: user not member project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=403, detail="Access denied")
    return project


async def update_project(
    db: AsyncSession,
    *,
    project_id: UUID,
    data: UpdateProjectRequest,
    current_user: User,
) -> None:
    """Update project metadata (owner only)."""
    project = await _get_owned_project(db, project_id, current_user)

    if data.name is not None:
        project.name = data.name.strip()
    if data.description is not None:
        project.description = data.description

    db.add(project)
    await db.commit()
    logger.info("Project updated project_id=%s user_id=%s", project_id, current_user.id)


async def list_members(
    db: AsyncSession,
    *,
    project_id: UUID,
    current_user: User,
) -> list[dict]:
    """List project members (requires membership)."""
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        logger.warning(
            "Member list failed: project not found project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="Project not found")

    membership = await repositories.project_repo.get_user_project(
        db, current_user.id, project_id
    )
    if membership is None:
        logger.warning(
            "Member list denied: user not member project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=403, detail="Access denied")

    rows = await repositories.project_repo.list_members(db, project_id)
    return [
        {
            "user_id": user.id,
            "username": user.username,
            "role_id": role.id,
            "role_name": role.name,
        }
        for user, role in rows
    ]


async def add_member(
    db: AsyncSession,
    *,
    project_id: UUID,
    data: AddProjectMemberRequest,
    current_user: User,
) -> None:
    """Add a user to a project with a specific role (owner only)."""
    await _get_owned_project(db, project_id, current_user)

    user = await repositories.user_repo.get_user_by_id(db, data.user_id)
    if user is None:
        logger.warning(
            "Add member failed: target user not found target_user_id=%s project_id=%s",
            data.user_id,
            project_id,
        )
        raise HTTPException(status_code=404, detail="User not found")

    role = await repositories.project_repo.get_role_by_id(db, data.role_id)
    if role is None or role.project_id != project_id:
        logger.warning(
            "Add member failed: role not found role_id=%s project_id=%s",
            data.role_id,
            project_id,
        )
        raise HTTPException(status_code=404, detail="Role not found in this project")

    existing = await repositories.project_repo.get_user_project(
        db, data.user_id, project_id
    )
    if existing is not None:
        logger.warning(
            "Add member failed: user already member target_user_id=%s project_id=%s",
            data.user_id,
            project_id,
        )
        raise HTTPException(
            status_code=409, detail="User is already a member of this project"
        )

    await repositories.project_repo.create_user_project(
        db,
        user_id=data.user_id,
        project_id=project_id,
        role_id=data.role_id,
    )
    await db.commit()
    logger.info(
        "Member added to project target_user_id=%s project_id=%s",
        data.user_id,
        project_id,
    )


async def change_member_role(
    db: AsyncSession,
    *,
    project_id: UUID,
    user_id: UUID,
    data: AssignRoleRequest,
    current_user: User,
) -> None:
    """Change a project member's role (owner only)."""
    await _get_owned_project(db, project_id, current_user)

    role = await repositories.project_repo.get_role_by_id(db, data.role_id)
    if role is None or role.project_id != project_id:
        logger.warning(
            "Role change failed: role not found role_id=%s project_id=%s",
            data.role_id,
            project_id,
        )
        raise HTTPException(status_code=404, detail="Role not found in this project")

    membership = await repositories.project_repo.get_user_project(
        db, user_id, project_id
    )
    if membership is None:
        logger.warning(
            "Role change failed: target user not member target_user_id=%s project_id=%s",
            user_id,
            project_id,
        )
        raise HTTPException(
            status_code=404, detail="User is not a member of this project"
        )

    await repositories.project_repo.update_user_project_role(
        db, membership=membership, role_id=data.role_id
    )
    await db.commit()
    logger.info(
        "Member role changed target_user_id=%s project_id=%s role_id=%s",
        user_id,
        project_id,
        data.role_id,
    )


async def _get_owned_project(
    db: AsyncSession, project_id: UUID, current_user: User
) -> Project:
    """Helper: get project and verify current user is its owner.

    MVP: authorization through owner FK comparison (without full RBAC).
    """
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        logger.warning(
            "Project operation failed: project not found project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="Project not found")
    if project.project_owner_id != current_user.id:
        logger.warning(
            "Project operation denied: user not owner project_id=%s user_id=%s",
            project_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=403, detail="Only project owner can perform this operation"
        )
    return project
