from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.role.request import (
    RolePermissions,
    CreateRoleRequest,
    UpdateRoleRequest,
)
from api.schemas.role.response import (
    RoleListResponse,
    RoleResponse,
)
from api.schemas.common.base import CreatedIdResponse
from db.models.user import User


router = APIRouter(prefix="/projects/{project_id}/roles", tags=["Roles"])


@router.get("", response_model=RoleListResponse)
async def get_roles(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RoleListResponse(items=[], total=0, offset=0, limit=20)


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    project_id: UUID,
    body: CreateRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    project_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RoleResponse(
        id=role_id,
        name="Test Role",
        permissions=RolePermissions(
            can_write_tickets=True,
            can_help=False,
            can_assign_help=False,
            can_change_status=False,
            can_make_roles=False,
            can_change_roles=False,
            can_assign_people_to_project=False,
        ),
    )


@router.patch("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_role(
    project_id: UUID,
    role_id: UUID,
    body: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return
