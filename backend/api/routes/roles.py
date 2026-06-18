from uuid import UUID

from db.models.role import Role
from db.models.user import User
from fastapi import APIRouter, Depends, status
from services import role_service
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.schemas.common.base import CreatedIdResponse
from api.schemas.role.request import (
    CreateRoleRequest,
    RolePermissions,
    UpdateRoleRequest,
)
from api.schemas.role.response import (
    RoleListResponse,
    RoleResponse,
)

router = APIRouter(prefix="/projects/{project_id}/roles", tags=["Roles"])


def _to_response(role: Role) -> RoleResponse:
    """Maps a Role model to API response."""
    return RoleResponse(
        id=role.id,
        name=role.name,
        permissions=RolePermissions(
            can_write_tickets=role.can_write_tickets,
            can_help=role.can_help,
            can_assign_help=role.can_assign_help,
            can_change_status=role.can_change_status,
            can_make_roles=role.can_make_roles,
            can_change_roles=role.can_change_roles,
            can_assign_people_to_project=role.can_assign_people_to_project,
        ),
    )


@router.get("", response_model=RoleListResponse)
async def get_roles(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists roles in a project."""
    roles = await role_service.list_roles(
        db, project_id=project_id, current_user=current_user
    )
    items = [_to_response(r) for r in roles]
    return RoleListResponse(items=items, total=len(items), offset=0, limit=len(items))


@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    project_id: UUID,
    body: CreateRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Creates a role. Project owner only."""
    role = await role_service.create_role(
        db, project_id=project_id, data=body, current_user=current_user
    )
    return CreatedIdResponse(id=role.id)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    project_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns one role."""
    role = await role_service.get_role(
        db, project_id=project_id, role_id=role_id, current_user=current_user
    )
    return _to_response(role)


@router.patch("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_role(
    project_id: UUID,
    role_id: UUID,
    body: UpdateRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Updates a role. Project owner only."""
    await role_service.update_role(
        db, project_id=project_id, role_id=role_id, data=body, current_user=current_user
    )
    return
