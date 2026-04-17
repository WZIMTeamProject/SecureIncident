from fastapi import APIRouter, status, Query, Path, Response
from typing import Optional
from uuid import UUID

from api.schemas.common.base import CreatedIdResponse
from api.schemas.project.request import (
    CreateProjectRequest,
    UpdateProjectRequest,
    AddProjectMemberRequest,
    AssignRoleRequest,
    ProjectScope
)
from api.schemas.project.response import (
    ProjectResponse,
    ProjectListResponse,
    ProjectMemberListResponse,
    ProjectMemberResponse
)

router = APIRouter(prefix="/projects", tags=["Projects"])



@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: CreateProjectRequest):
    # TODO:
    # - sprawdzić scope (PRIVATE / ORGANIZATION)
    # - przypisać ownera
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")



@router.get("", response_model=ProjectListResponse)
def list_projects(scope: Optional[ProjectScope] = Query(None)):
    # TODO:
    # - filtrowanie po scope (PRIVATE / ORGANIZATION)

    return ProjectListResponse(
        projects=[
            ProjectResponse(
                id="00000000-0000-0000-0000-000000000000",
                organizationId=None,
                name="Test Project",
                description="Test",
                scope=ProjectScope.PRIVATE
            )
        ]
    )



@router.get("/{projectId}", response_model=ProjectResponse)
def get_project(projectId: UUID = Path(...)):
    # TODO:
    # - sprawdzić dostęp
    return ProjectResponse(
        id=projectId,
        organizationId=None,
        name="Test Project",
        description="Test",
        scope=ProjectScope.PRIVATE
    )



@router.patch("/{projectId}", status_code=status.HTTP_204_NO_CONTENT)
def update_project(projectId: UUID,data: UpdateProjectRequest):

    # TODO:
    # - update name / description
    return Response(status_code=204)



@router.get("/{projectId}/members", response_model=ProjectMemberListResponse)
def list_members(projectId: UUID):
    # TO DO: return ProjectMemberListResponse(members=[])
    return ProjectMemberListResponse(
        members=[
            ProjectMemberResponse(
                userId="00000000-0000-0000-0000-000000000000",
                username="test_user",
                roleId="00000000-0000-0000-0000-000000000000",
                roleName="Admin"
            )
        ]
    )



@router.post("/{projectId}/members", status_code=status.HTTP_204_NO_CONTENT)
def add_member(projectId: UUID,data: AddProjectMemberRequest):
    # TODO:
    # - sprawdzić czy user istnieje
    # - czy już jest w projekcie (409)
    return Response(status_code=204)



@router.patch("/{projectId}/members/{userId}/role", status_code=status.HTTP_204_NO_CONTENT)
def change_member_role(projectId: UUID,userId: UUID,data: AssignRoleRequest):
    # TODO:
    # - zmiana roli
    return Response(status_code=204)