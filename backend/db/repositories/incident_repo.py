from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.incident import Incident
from db.models.incident_helper import IncidentHelper
from db.models.incident_log import IncidentLog
from db.models.comment import Comment


async def get_by_id(db: AsyncSession, incident_id: UUID) -> Optional[Incident]:
    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .options(
            selectinload(Incident.reporter),
            selectinload(Incident.primary_assignee),
            selectinload(Incident.category),
            selectinload(Incident.helpers).selectinload(IncidentHelper.user),
        )
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def get_incidents_by_project(
    db: AsyncSession,
    project_id: UUID,
    *,
    offset: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
) -> tuple[Sequence[Incident], int]:
    count_stmt = select(func.count()).select_from(Incident).where(Incident.project_id == project_id)
    data_stmt = select(Incident).where(Incident.project_id == project_id)

    if status is not None:
        count_stmt = count_stmt.where(Incident.status == status)
        data_stmt = data_stmt.where(Incident.status == status)
    if priority is not None:
        count_stmt = count_stmt.where(Incident.priority == priority)
        data_stmt = data_stmt.where(Incident.priority == priority)
    if assignee_id is not None:
        count_stmt = count_stmt.where(Incident.primary_assignee_id == assignee_id)
        data_stmt = data_stmt.where(Incident.primary_assignee_id == assignee_id)

    total = (await db.execute(count_stmt)).scalar_one()
    data_stmt = data_stmt.order_by(Incident.created_at.desc()).offset(offset).limit(limit)
    incidents = (await db.execute(data_stmt)).scalars().all()
    return incidents, total


async def get_by_reporter(
    db: AsyncSession,
    user_id: UUID,
    *,
    offset: int = 0,
    limit: int = 20,
) -> tuple[Sequence[Incident], int]:
    count_stmt = select(func.count()).select_from(Incident).where(Incident.reporter_id == user_id)
    total = (await db.execute(count_stmt)).scalar_one()
    data_stmt = (
        select(Incident)
        .where(Incident.reporter_id == user_id)
        .order_by(Incident.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return (await db.execute(data_stmt)).scalars().all(), total


async def get_by_assignee(
    db: AsyncSession,
    user_id: UUID,
    *,
    offset: int = 0,
    limit: int = 20,
) -> tuple[Sequence[Incident], int]:
    count_stmt = select(func.count()).select_from(Incident).where(Incident.primary_assignee_id == user_id)
    total = (await db.execute(count_stmt)).scalar_one()
    data_stmt = (
        select(Incident)
        .where(Incident.primary_assignee_id == user_id)
        .order_by(Incident.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return (await db.execute(data_stmt)).scalars().all(), total


async def create(db: AsyncSession, incident: Incident) -> None:
    db.add(incident)
    await db.flush()


async def update(db: AsyncSession, incident: Incident) -> None:
    db.add(incident)
    await db.flush()


async def get_comments_by_incident(
    db: AsyncSession, incident_id: UUID
) -> Sequence[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.incident_id == incident_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc())
    )
    return result.scalars().all()


async def create_comment(db: AsyncSession, comment: Comment) -> None:
    db.add(comment)
    await db.flush()


async def get_logs_by_incident(
    db: AsyncSession,
    incident_id: UUID,
    *,
    offset: int = 0,
    limit: int = 20,
    type_filter: Optional[list[str]] = None,
) -> tuple[Sequence[IncidentLog], int]:
    count_stmt = (
        select(func.count())
        .select_from(IncidentLog)
        .where(IncidentLog.incident_id == incident_id)
    )
    data_stmt = select(IncidentLog).where(IncidentLog.incident_id == incident_id)

    if type_filter is not None:
        count_stmt = count_stmt.where(IncidentLog.type.in_(type_filter))
        data_stmt = data_stmt.where(IncidentLog.type.in_(type_filter))

    total = (await db.execute(count_stmt)).scalar_one()
    data_stmt = data_stmt.order_by(IncidentLog.created_at.asc()).offset(offset).limit(limit)
    logs = (await db.execute(data_stmt)).scalars().all()
    return logs, total


async def get_logs_by_user(
    db: AsyncSession,
    user_id: UUID,
    *,
    project_id: Optional[UUID] = None,
    log_type: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[Sequence[IncidentLog], int]:
    base_filter = [IncidentLog.person_id == user_id]

    count_stmt = (
        select(func.count())
        .select_from(IncidentLog)
        .join(Incident, IncidentLog.incident_id == Incident.id)
        .where(*base_filter)
    )
    data_stmt = (
        select(IncidentLog)
        .join(Incident, IncidentLog.incident_id == Incident.id)
        .where(*base_filter)
    )

    if project_id is not None:
        count_stmt = count_stmt.where(Incident.project_id == project_id)
        data_stmt = data_stmt.where(Incident.project_id == project_id)
    if log_type is not None:
        count_stmt = count_stmt.where(IncidentLog.type == log_type)
        data_stmt = data_stmt.where(IncidentLog.type == log_type)

    total = (await db.execute(count_stmt)).scalar_one()
    data_stmt = data_stmt.order_by(IncidentLog.created_at.desc()).offset(offset).limit(limit)
    logs = (await db.execute(data_stmt)).scalars().all()
    return logs, total


async def create_log(db: AsyncSession, log: IncidentLog) -> None:
    db.add(log)
    await db.flush()


async def get_helper(
    db: AsyncSession, incident_id: UUID, user_id: UUID
) -> Optional[IncidentHelper]:
    result = await db.execute(
        select(IncidentHelper).where(
            IncidentHelper.incident_id == incident_id,
            IncidentHelper.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def create_helper(db: AsyncSession, helper: IncidentHelper) -> None:
    db.add(helper)
    await db.flush()


async def delete_helper(db: AsyncSession, helper: IncidentHelper) -> None:
    await db.delete(helper)
    await db.flush()
