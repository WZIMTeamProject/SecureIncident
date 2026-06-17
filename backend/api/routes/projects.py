from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status, Query, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.common.base import CreatedIdResponse
from api.schemas.project.request import (
    CreateProjectRequest,
    UpdateProjectRequest,
    AddProjectMemberRequest,
    AssignRoleRequest,
    ProjectScope,
)
from api.schemas.project.response import (
    ProjectResponse,
    ProjectListResponse,
    ProjectMemberListResponse,
    ProjectMemberResponse,
)
from db.models.user import User
from services import project_service


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a project (atomically: project + Owner role + owner membership)."""
    project = await project_service.create_project(
        db, data=data, current_user=current_user
    )
    return CreatedIdResponse(id=project.id)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    scope: Optional[ProjectScope] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List projects the current user is a member of."""
    projects = await project_service.list_projects(
        db, current_user=current_user, scope=scope
    )
    items = [
        ProjectResponse(
            id=p.id,
            organization_id=p.organization_id,
            name=p.name,
            description=p.description,
            scope=ProjectScope(p.scope),
        )
        for p in projects
    ]
    return ProjectListResponse(
        items=items, total=len(items), offset=0, limit=len(items)
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project details (requires membership)."""
    project = await project_service.get_project(
        db, project_id=project_id, current_user=current_user
    )
    return ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        name=project.name,
        description=project.description,
        scope=ProjectScope(project.scope),
    )


@router.patch("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_project(
    project_id: UUID,
    data: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project metadata (owner only)."""
    await project_service.update_project(
        db, project_id=project_id, data=data, current_user=current_user
    )
    return Response(status_code=204)


@router.get("/{project_id}/members", response_model=ProjectMemberListResponse)
async def list_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project members (requires membership)."""
    members = await project_service.list_members(
        db, project_id=project_id, current_user=current_user
    )
    return ProjectMemberListResponse(
        members=[ProjectMemberResponse(**m) for m in members]
    )


@router.post("/{project_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_member(
    project_id: UUID,
    data: AddProjectMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a user to the project (owner only)."""
    await project_service.add_member(
        db, project_id=project_id, data=data, current_user=current_user
    )
    return Response(status_code=204)


@router.patch("/{project_id}/members/{user_id}/role", status_code=status.HTTP_204_NO_CONTENT)
async def change_member_role(
    project_id: UUID,
    user_id: UUID,
    data: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change a member's role in the project (owner only)."""
    await project_service.change_member_role(
        db, project_id=project_id, user_id=user_id, data=data, current_user=current_user
    )
    return Response(status_code=204)