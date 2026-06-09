from fastapi import APIRouter, Depends, status
from uuid import UUID
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.common.base import CreatedIdResponse
from api.schemas.incident.request import (
    CreateIncidentRequest,
    UpdateIncidentStatusRequest,
    UpdateIncidentAssigneeRequest,
    UpdateIncidentPriorityRequest,
    UpdateIncidentCategoryRequest,
    AddCommentRequest,
    AddHelperRequest,
)
from api.schemas.incident.response import (
    IncidentListResponse,
    IncidentDetailsResponse,
)
from api.schemas.incident.comment import CommentListResponse
from api.schemas.incident.log import IncidentLogListResponse
from api.schemas.common.enums import (
    IncidentPriority,
    IncidentStatus,
    IncidentLogType,
)
from db.models.user import User


router = APIRouter(tags=["Incidents"])


@router.get("/projects/{project_id}/incidents", response_model=IncidentListResponse)
async def get_incidents(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return IncidentListResponse(items=[], total=0, offset=0, limit=20)


@router.post("/projects/{project_id}/incidents", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    project_id: UUID,
    body: CreateIncidentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("/incidents/my-reported", response_model=IncidentListResponse)
async def get_my_reported(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return IncidentListResponse(items=[], total=0, offset=0, limit=20)


@router.get("/incidents/my-assigned", response_model=IncidentListResponse)
async def get_my_assigned(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return IncidentListResponse(items=[], total=0, offset=0, limit=20)


@router.get("/incidents/history", response_model=IncidentLogListResponse)
async def get_incident_history(
    project_id: Optional[UUID] = None,
    type: Optional[IncidentLogType] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return IncidentLogListResponse(items=[], total=0, offset=0, limit=20)


@router.get("/incidents/{incident_id}", response_model=IncidentDetailsResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return IncidentDetailsResponse(
        id=incident_id,
        project_id="00000000-0000-0000-0000-000000000000",
        title="Test incident",
        description="Test description",
        category_id=None,
        priority=IncidentPriority.LOW,
        status=IncidentStatus.NEW,
        reporter_id="00000000-0000-0000-0000-000000000000",
        primary_assignee_id=None,
        report_date=datetime.now(),
    )


@router.patch("/incidents/{incident_id}/status", status_code=status.HTTP_204_NO_CONTENT)
async def update_incident_status(
    incident_id: UUID,
    body: UpdateIncidentStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.patch("/incidents/{incident_id}/assignee", status_code=status.HTTP_204_NO_CONTENT)
async def update_incident_assignee(
    incident_id: UUID,
    body: UpdateIncidentAssigneeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.patch("/incidents/{incident_id}/priority", status_code=status.HTTP_204_NO_CONTENT)
async def update_incident_priority(
    incident_id: UUID,
    body: UpdateIncidentPriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.patch("/incidents/{incident_id}/category", status_code=status.HTTP_204_NO_CONTENT)
async def update_incident_category(
    incident_id: UUID,
    body: UpdateIncidentCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.post("/incidents/{incident_id}/close", status_code=status.HTTP_204_NO_CONTENT)
async def close_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.post("/incidents/{incident_id}/request-reassignment", status_code=status.HTTP_204_NO_CONTENT)
async def request_reassignment(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.post("/incidents/{incident_id}/helpers", status_code=status.HTTP_204_NO_CONTENT)
async def add_helper(
    incident_id: UUID,
    body: AddHelperRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.delete("/incidents/{incident_id}/helpers/{helper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_helper(
    incident_id: UUID,
    helper_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return


@router.get("/incidents/{incident_id}/comments", response_model=CommentListResponse)
async def get_comments(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommentListResponse(comments=[])


@router.post("/incidents/{incident_id}/comments", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    incident_id: UUID,
    body: AddCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("/incidents/{incident_id}/logs", response_model=IncidentLogListResponse)
async def get_logs(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return IncidentLogListResponse(items=[], total=0, offset=0, limit=20)
