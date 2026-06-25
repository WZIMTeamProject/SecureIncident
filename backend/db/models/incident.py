import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_reporter_id", "reporter_id"),
        Index("ix_incidents_primary_assignee_id", "primary_assignee_id"),
        Index("ix_incidents_project_id", "project_id"),
        Index("ix_incidents_category_id", "category_id"),
        Index("ix_incidents_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    primary_assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="NEW", nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="LOW", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    closing_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    reporter: Mapped[User] = relationship(
        "User", back_populates="incidents", foreign_keys=[reporter_id], lazy="selectin"
    )
    primary_assignee: Mapped[User | None] = relationship(
        "User",
        back_populates="assigned_incidents",
        foreign_keys=[primary_assignee_id],
        lazy="selectin",
    )
    project: Mapped[Project] = relationship(
        "Project",
        back_populates="incidents",
        foreign_keys=[project_id],
        lazy="selectin",
    )
    category: Mapped[Category | None] = relationship(
        "Category", back_populates="incidents", lazy="selectin"
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="incident",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    logs: Mapped[list[IncidentLog]] = relationship(
        "IncidentLog",
        back_populates="incident",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    helpers: Mapped[list[IncidentHelper]] = relationship(
        "IncidentHelper",
        back_populates="incident",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
