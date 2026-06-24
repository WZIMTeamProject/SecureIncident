from uuid import UUID

from db.models.user import User
from fastapi import APIRouter, Depends, Query, status
from services import incident_service
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.schemas.common.base import CreatedIdResponse
from api.schemas.common.enums import (
    IncidentLogType,
    IncidentPriority,
    IncidentStatus,
)
from api.schemas.incident.comment import CommentListResponse
from api.schemas.incident.log import IncidentLogListResponse
from api.schemas.incident.request import (
    AddCommentRequest,
    AddHelperRequest,
    CreateIncidentRequest,
    UpdateIncidentAssigneeRequest,
    UpdateIncidentCategoryRequest,
    UpdateIncidentPriorityRequest,
    UpdateIncidentStatusRequest,
)
from api.schemas.incident.response import (
    IncidentDetailsResponse,
    IncidentListResponse,
)

router = APIRouter(tags=["Incidents"])


@router.get("/projects/{project_id}/incidents", response_model=IncidentListResponse)
async def get_incidents(
    project_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status: IncidentStatus | None = None,
    priority: IncidentPriority | None = None,
    assignee_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.list_incidents(
        db,
        project_id,
        current_user,
        offset=offset,
        limit=limit,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        assignee_id=assignee_id,
    )


@router.post(
    "/projects/{project_id}/incidents",
    response_model=CreatedIdResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    project_id: UUID,
    body: CreateIncidentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.create_incident(db, project_id, body, current_user)


@router.get("/incidents/my-reported", response_model=IncidentListResponse)
async def get_my_reported(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.get_my_reported(
        db, current_user, offset=offset, limit=limit
    )


@router.get("/incidents/my-assigned", response_model=IncidentListResponse)
async def get_my_assigned(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.get_my_assigned(
        db, current_user, offset=offset, limit=limit
    )


@router.get("/incidents/history", response_model=IncidentLogListResponse)
async def get_incident_history(
    project_id: UUID | None = None,
    type: IncidentLogType | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.get_history(
        db,
        current_user,
        project_id=project_id,
        log_type=type.value if type else None,
        offset=offset,
        limit=limit,
    )


@router.get("/incidents/{incident_id}", response_model=IncidentDetailsResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.get_incident_detail(db, incident_id, current_user)


@router.patch("/incidents/{incident_id}/status", status_code=status.HTTP_204_NO_CONTENT)
async def update_incident_status(
    incident_id: UUID,
    body: UpdateIncidentStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.update_status(db, incident_id, body, current_user)


@router.patch(
    "/incidents/{incident_id}/assignee", status_code=status.HTTP_204_NO_CONTENT
)
async def update_incident_assignee(
    incident_id: UUID,
    body: UpdateIncidentAssigneeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.update_assignee(db, incident_id, body, current_user)


@router.patch(
    "/incidents/{incident_id}/priority", status_code=status.HTTP_204_NO_CONTENT
)
async def update_incident_priority(
    incident_id: UUID,
    body: UpdateIncidentPriorityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.update_priority(db, incident_id, body, current_user)


@router.patch(
    "/incidents/{incident_id}/category", status_code=status.HTTP_204_NO_CONTENT
)
async def update_incident_category(
    incident_id: UUID,
    body: UpdateIncidentCategoryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.update_category(db, incident_id, body, current_user)


@router.post("/incidents/{incident_id}/close", status_code=status.HTTP_204_NO_CONTENT)
async def close_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.close_incident(db, incident_id, current_user)


@router.post(
    "/incidents/{incident_id}/request-reassignment",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def request_reassignment(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.request_reassignment(db, incident_id, current_user)


@router.post("/incidents/{incident_id}/helpers", status_code=status.HTTP_204_NO_CONTENT)
async def add_helper(
    incident_id: UUID,
    body: AddHelperRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.add_helper(db, incident_id, body, current_user)


@router.delete(
    "/incidents/{incident_id}/helpers/{helper_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_helper(
    incident_id: UUID,
    helper_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await incident_service.remove_helper(db, incident_id, helper_id, current_user)


@router.get("/incidents/{incident_id}/comments", response_model=CommentListResponse)
async def get_comments(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.get_comments(db, incident_id, current_user)


@router.post(
    "/incidents/{incident_id}/comments",
    response_model=CreatedIdResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    incident_id: UUID,
    body: AddCommentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.add_comment(db, incident_id, body, current_user)


@router.get("/incidents/{incident_id}/logs", response_model=IncidentLogListResponse)
async def get_logs(
    incident_id: UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await incident_service.get_logs(
        db, incident_id, current_user, offset=offset, limit=limit
    )
