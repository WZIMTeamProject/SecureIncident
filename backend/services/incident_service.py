import logging
from datetime import UTC, datetime
from uuid import UUID

from api.schemas.common.base import CreatedIdResponse
from api.schemas.common.enums import IncidentLogType, IncidentPriority, IncidentStatus
from api.schemas.incident.comment import CommentListResponse, CommentResponse
from api.schemas.incident.log import IncidentLogEntry, IncidentLogListResponse
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
    HelperResponse,
    IncidentDetailsResponse,
    IncidentListResponse,
    IncidentSummary,
)
from db import repositories
from db.models.comment import Comment
from db.models.incident import Incident
from db.models.incident_helper import IncidentHelper
from db.models.incident_log import IncidentLog
from db.models.user import User
from db.models.user_project import UserProject
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def _get_incident_or_404(db: AsyncSession, incident_id: UUID) -> Incident:
    inc = await repositories.incident_repo.get_by_id(db, incident_id)
    if inc is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc


async def _get_membership_or_403(
    db: AsyncSession, project_id: UUID, user_id: UUID
) -> UserProject:
    m = await repositories.project_repo.get_user_project(db, user_id, project_id)
    if m is None:
        logger.warning(
            "Incident access denied: user not project member project_id=%s user_id=%s",
            project_id,
            user_id,
        )
        raise HTTPException(status_code=403, detail="Not a project member")
    return m


def _require_flag(membership: UserProject, flag: str) -> None:
    if not getattr(membership.role, flag, False):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


async def create_incident(
    db: AsyncSession,
    project_id: UUID,
    data: CreateIncidentRequest,
    current_user: User,
) -> CreatedIdResponse:
    membership = await _get_membership_or_403(db, project_id, current_user.id)
    _require_flag(membership, "can_write_tickets")

    if data.category_id is not None:
        cat = await repositories.category_repo.get_by_id(db, data.category_id)
        if cat is None or cat.project_id != project_id:
            logger.warning(
                "Incident create failed: category not found category_id=%s project_id=%s user_id=%s",
                data.category_id,
                project_id,
                current_user.id,
            )
            raise HTTPException(
                status_code=404, detail="Category not found in this project"
            )

    if data.primary_assignee_id is not None:
        if (
            await repositories.project_repo.get_user_project(
                db, data.primary_assignee_id, project_id
            )
            is None
        ):
            logger.warning(
                "Incident create failed: assignee not project member assignee_id=%s project_id=%s user_id=%s",
                data.primary_assignee_id,
                project_id,
                current_user.id,
            )
            raise HTTPException(
                status_code=422, detail="Assignee is not a project member"
            )

    incident = Incident(
        reporter_id=current_user.id,
        project_id=project_id,
        title=data.title,
        description=data.description,
        status=IncidentStatus.NEW.value,
        priority=data.priority.value if data.priority else IncidentPriority.LOW.value,
        category_id=data.category_id,
        primary_assignee_id=data.primary_assignee_id,
    )
    await repositories.incident_repo.create(db, incident)

    log = IncidentLog(
        incident_id=incident.id,
        person_id=current_user.id,
        type=IncidentLogType.CREATED.value,
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    await db.refresh(incident)
    logger.info(
        "Incident created incident_id=%s project_id=%s user_id=%s",
        incident.id,
        project_id,
        current_user.id,
    )
    return CreatedIdResponse(id=incident.id)


async def list_incidents(
    db: AsyncSession,
    project_id: UUID,
    current_user: User,
    *,
    offset: int = 0,
    limit: int = 20,
    status: str | None = None,
    priority: str | None = None,
    assignee_id: UUID | None = None,
) -> IncidentListResponse:
    await _get_membership_or_403(db, project_id, current_user.id)
    incidents, total = await repositories.incident_repo.get_incidents_by_project(
        db,
        project_id,
        offset=offset,
        limit=limit,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
    )
    items = [
        IncidentSummary(
            id=i.id,
            title=i.title,
            status=i.status,
            priority=i.priority,
            primary_assignee_id=i.primary_assignee_id,
            category_id=i.category_id,
            report_date=i.created_at,
        )
        for i in incidents
    ]
    return IncidentListResponse(items=items, total=total, limit=limit, offset=offset)


async def get_incident_detail(
    db: AsyncSession,
    incident_id: UUID,
    current_user: User,
) -> IncidentDetailsResponse:
    incident = await _get_incident_or_404(db, incident_id)
    await _get_membership_or_403(db, incident.project_id, current_user.id)
    helpers = [
        HelperResponse(user_id=h.user_id, added_at=h.added_at) for h in incident.helpers
    ]
    return IncidentDetailsResponse(
        id=incident.id,
        title=incident.title,
        description=incident.description,
        status=incident.status,
        priority=incident.priority,
        reporter_id=incident.reporter_id,
        primary_assignee_id=incident.primary_assignee_id,
        project_id=incident.project_id,
        category_id=incident.category_id,
        report_date=incident.created_at,
        closing_date=incident.closing_date,
        helpers=helpers,
    )


async def get_my_reported(
    db: AsyncSession,
    current_user: User,
    *,
    offset: int = 0,
    limit: int = 20,
) -> IncidentListResponse:
    incidents, total = await repositories.incident_repo.get_by_reporter(
        db, current_user.id, offset=offset, limit=limit
    )
    items = [
        IncidentSummary(
            id=i.id,
            title=i.title,
            status=i.status,
            priority=i.priority,
            primary_assignee_id=i.primary_assignee_id,
            category_id=i.category_id,
            report_date=i.created_at,
        )
        for i in incidents
    ]
    return IncidentListResponse(items=items, total=total, limit=limit, offset=offset)


async def get_my_assigned(
    db: AsyncSession,
    current_user: User,
    *,
    offset: int = 0,
    limit: int = 20,
) -> IncidentListResponse:
    incidents, total = await repositories.incident_repo.get_by_assignee(
        db, current_user.id, offset=offset, limit=limit
    )
    items = [
        IncidentSummary(
            id=i.id,
            title=i.title,
            status=i.status,
            priority=i.priority,
            primary_assignee_id=i.primary_assignee_id,
            category_id=i.category_id,
            report_date=i.created_at,
        )
        for i in incidents
    ]
    return IncidentListResponse(items=items, total=total, limit=limit, offset=offset)


async def update_status(
    db: AsyncSession,
    incident_id: UUID,
    data: UpdateIncidentStatusRequest,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_change_status")

    if incident.status == IncidentStatus.CLOSED.value:
        logger.warning(
            "Status update rejected: incident is closed incident_id=%s user_id=%s",
            incident_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=409, detail="Cannot change status of a closed incident"
        )

    old_status = incident.status
    incident.status = data.status.value
    if data.status != IncidentStatus.CLOSED:
        incident.closing_date = None
    await repositories.incident_repo.update(db, incident)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.STATUS_CHANGED.value,
        old_value=old_status,
        new_value=data.status.value,
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Incident status changed incident_id=%s old=%s new=%s user_id=%s",
        incident_id,
        old_status,
        data.status.value,
        current_user.id,
    )


async def update_priority(
    db: AsyncSession,
    incident_id: UUID,
    data: UpdateIncidentPriorityRequest,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_change_status")

    old_priority = incident.priority
    incident.priority = data.priority.value
    await repositories.incident_repo.update(db, incident)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.PRIORITY_CHANGED.value,
        old_value=old_priority,
        new_value=data.priority.value,
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Incident priority changed incident_id=%s old=%s new=%s user_id=%s",
        incident_id,
        old_priority,
        data.priority.value,
        current_user.id,
    )


async def update_assignee(
    db: AsyncSession,
    incident_id: UUID,
    data: UpdateIncidentAssigneeRequest,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_assign_help")

    if data.primary_assignee_id is not None:
        if (
            await repositories.project_repo.get_user_project(
                db, data.primary_assignee_id, incident.project_id
            )
            is None
        ):
            logger.warning(
                "Incident assignee update failed: assignee not project member assignee_id=%s incident_id=%s user_id=%s",
                data.primary_assignee_id,
                incident_id,
                current_user.id,
            )
            raise HTTPException(
                status_code=422, detail="Assignee is not a project member"
            )

    incident.primary_assignee_id = data.primary_assignee_id
    await repositories.incident_repo.update(db, incident)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.ASSIGNEE_CHANGED.value,
        new_value=str(data.primary_assignee_id)
        if data.primary_assignee_id is not None
        else "",
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Incident assignee changed incident_id=%s new_assignee_id=%s user_id=%s",
        incident_id,
        data.primary_assignee_id,
        current_user.id,
    )


async def update_category(
    db: AsyncSession,
    incident_id: UUID,
    data: UpdateIncidentCategoryRequest,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_help")

    cat = await repositories.category_repo.get_by_id(db, data.category_id)
    if cat is None or cat.project_id != incident.project_id:
        logger.warning(
            "Incident category update failed: category not found category_id=%s incident_id=%s user_id=%s",
            data.category_id,
            incident_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=404, detail="Category not found in this project"
        )

    incident.category_id = data.category_id
    await repositories.incident_repo.update(db, incident)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.CATEGORY_CHANGED.value,
        new_value=str(data.category_id),
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Incident category changed incident_id=%s category_id=%s user_id=%s",
        incident_id,
        data.category_id,
        current_user.id,
    )


async def close_incident(
    db: AsyncSession,
    incident_id: UUID,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_change_status")

    if incident.status == IncidentStatus.CLOSED.value:
        logger.warning(
            "Incident close failed: already closed incident_id=%s user_id=%s",
            incident_id,
            current_user.id,
        )
        raise HTTPException(status_code=409, detail="Incident is already closed")

    incident.status = IncidentStatus.CLOSED.value
    # Use datetime.now(timezone.utc).replace(tzinfo=None) — NOT utcnow() which is deprecated
    incident.closing_date = datetime.now(UTC).replace(tzinfo=None)
    await repositories.incident_repo.update(db, incident)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.CLOSED.value,
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Incident closed incident_id=%s user_id=%s", incident_id, current_user.id
    )


async def request_reassignment(
    db: AsyncSession,
    incident_id: UUID,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_help")

    existing = await repositories.incident_repo.get_helper(
        db, incident_id, current_user.id
    )
    if existing is not None:
        logger.warning(
            "Reassignment request failed: already a helper incident_id=%s user_id=%s",
            incident_id,
            current_user.id,
        )
        raise HTTPException(status_code=409, detail="Already a helper on this incident")

    helper = IncidentHelper(incident_id=incident_id, user_id=current_user.id)
    await repositories.incident_repo.create_helper(db, helper)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.HELPER_ADDED.value,
        new_value=str(current_user.id),
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Helper self-added incident_id=%s user_id=%s", incident_id, current_user.id
    )


async def add_helper(
    db: AsyncSession,
    incident_id: UUID,
    data: AddHelperRequest,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_assign_help")

    if (
        await repositories.project_repo.get_user_project(
            db, data.user_id, incident.project_id
        )
        is None
    ):
        logger.warning(
            "Add helper failed: target user not project member target_user_id=%s incident_id=%s user_id=%s",
            data.user_id,
            incident_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=422, detail="Target user is not a project member"
        )

    existing = await repositories.incident_repo.get_helper(
        db, incident_id, data.user_id
    )
    if existing is not None:
        logger.warning(
            "Add helper failed: user already a helper target_user_id=%s incident_id=%s user_id=%s",
            data.user_id,
            incident_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=409, detail="User is already a helper on this incident"
        )

    helper = IncidentHelper(incident_id=incident_id, user_id=data.user_id)
    await repositories.incident_repo.create_helper(db, helper)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.HELPER_ADDED.value,
        new_value=str(data.user_id),
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Helper added incident_id=%s helper_id=%s user_id=%s",
        incident_id,
        data.user_id,
        current_user.id,
    )


async def remove_helper(
    db: AsyncSession,
    incident_id: UUID,
    helper_id: UUID,
    current_user: User,
) -> None:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)
    _require_flag(membership, "can_assign_help")

    helper = await repositories.incident_repo.get_helper(db, incident_id, helper_id)
    if helper is None:
        logger.warning(
            "Remove helper failed: helper not found helper_id=%s incident_id=%s user_id=%s",
            helper_id,
            incident_id,
            current_user.id,
        )
        raise HTTPException(status_code=404, detail="Helper not found")

    await repositories.incident_repo.delete_helper(db, helper)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.HELPER_REMOVED.value,
        old_value=str(helper_id),
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    logger.info(
        "Helper removed incident_id=%s helper_id=%s user_id=%s",
        incident_id,
        helper_id,
        current_user.id,
    )


async def get_comments(
    db: AsyncSession,
    incident_id: UUID,
    current_user: User,
) -> CommentListResponse:
    incident = await _get_incident_or_404(db, incident_id)
    await _get_membership_or_403(db, incident.project_id, current_user.id)

    if (
        incident.reporter_id != current_user.id
        and incident.primary_assignee_id != current_user.id
    ):
        logger.warning(
            "Get comments denied: user not reporter or assignee incident_id=%s user_id=%s",
            incident_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=403,
            detail="Only the reporter or primary assignee can view comments",
        )

    comments = await repositories.incident_repo.get_comments_by_incident(
        db, incident_id
    )
    items = [
        CommentResponse(
            id=c.id,
            author_id=c.author_id,
            author_username=c.author.username,
            content=c.content,
            created_at=c.created_at,
        )
        for c in comments
    ]
    return CommentListResponse(comments=items)


async def add_comment(
    db: AsyncSession,
    incident_id: UUID,
    data: AddCommentRequest,
    current_user: User,
) -> CreatedIdResponse:
    incident = await _get_incident_or_404(db, incident_id)
    await _get_membership_or_403(db, incident.project_id, current_user.id)

    if (
        incident.reporter_id != current_user.id
        and incident.primary_assignee_id != current_user.id
    ):
        logger.warning(
            "Add comment denied: user not reporter or assignee incident_id=%s user_id=%s",
            incident_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=403,
            detail="Only the reporter or primary assignee can add comments",
        )

    comment = Comment(
        incident_id=incident_id, author_id=current_user.id, content=data.content
    )
    await repositories.incident_repo.create_comment(db, comment)

    log = IncidentLog(
        incident_id=incident_id,
        person_id=current_user.id,
        type=IncidentLogType.COMMENT.value,
        comment=data.content[:500],
    )
    await repositories.incident_repo.create_log(db, log)
    await db.commit()
    await db.refresh(comment)
    logger.info(
        "Comment added incident_id=%s comment_id=%s user_id=%s",
        incident_id,
        comment.id,
        current_user.id,
    )
    return CreatedIdResponse(id=comment.id)


async def get_logs(
    db: AsyncSession,
    incident_id: UUID,
    current_user: User,
    *,
    offset: int = 0,
    limit: int = 20,
) -> IncidentLogListResponse:
    incident = await _get_incident_or_404(db, incident_id)
    membership = await _get_membership_or_403(db, incident.project_id, current_user.id)

    is_admin = getattr(membership.role, "can_assign_help", False) or getattr(
        membership.role, "can_change_status", False
    )
    if is_admin:
        type_filter = None
    else:
        type_filter = [
            IncidentLogType.COMMENT.value,
            IncidentLogType.STATUS_CHANGED.value,
            IncidentLogType.ASSIGNEE_CHANGED.value,
            IncidentLogType.CREATED.value,
            IncidentLogType.CLOSED.value,
        ]

    logs, total = await repositories.incident_repo.get_logs_by_incident(
        db, incident_id, offset=offset, limit=limit, type_filter=type_filter
    )
    items = [
        IncidentLogEntry(
            actor_id=log.person_id,
            id=log.id,
            incident_id=log.incident_id,
            type=log.type,
            comment=log.comment,
            old_value=log.old_value,
            new_value=log.new_value,
            created_at=log.created_at,
        )
        for log in logs
    ]
    return IncidentLogListResponse(items=items, total=total, limit=limit, offset=offset)


async def get_history(
    db: AsyncSession,
    current_user: User,
    *,
    project_id: UUID | None = None,
    log_type: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> IncidentLogListResponse:
    logs, total = await repositories.incident_repo.get_logs_by_user(
        db,
        current_user.id,
        project_id=project_id,
        log_type=log_type,
        offset=offset,
        limit=limit,
    )
    items = [
        IncidentLogEntry(
            actor_id=log.person_id,
            id=log.id,
            incident_id=log.incident_id,
            type=log.type,
            comment=log.comment,
            old_value=log.old_value,
            new_value=log.new_value,
            created_at=log.created_at,
        )
        for log in logs
    ]
    return IncidentLogListResponse(items=items, total=total, limit=limit, offset=offset)
