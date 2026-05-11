from fastapi import APIRouter, Depends, status, Query, Path, Response
from typing import Optional
from uuid import UUID
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


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: sprawdzić scope (PRIVATE / ORGANIZATION), przypisać ownera
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    scope: Optional[ProjectScope] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: filtrowanie po scope (PRIVATE / ORGANIZATION)
    return ProjectListResponse(items=[], total=0, offset=0, limit=20)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: sprawdzić dostęp
    return ProjectResponse(
        id=project_id,
        organization_id=None,
        name="Test Project",
        description="Test",
        scope=ProjectScope.PRIVATE,
    )


@router.patch("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_project(
    project_id: UUID,
    data: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: update name / description
    return Response(status_code=204)


@router.get("/{project_id}/members", response_model=ProjectMemberListResponse)
async def list_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: return members list
    return ProjectMemberListResponse(members=[])


@router.post("/{project_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_member(
    project_id: UUID,
    data: AddProjectMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: sprawdzić czy user istnieje, czy już jest w projekcie (409)
    return Response(status_code=204)


@router.patch("/{project_id}/members/{user_id}/role", status_code=status.HTTP_204_NO_CONTENT)
async def change_member_role(
    project_id: UUID,
    user_id: UUID,
    data: AssignRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: zmiana roli
    return Response(status_code=204)
