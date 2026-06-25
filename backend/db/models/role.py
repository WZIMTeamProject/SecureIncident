import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (Index("ix_roles_project_id", "project_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    can_write_tickets: Mapped[bool] = mapped_column(Boolean, default=False)
    can_help: Mapped[bool] = mapped_column(Boolean, default=False)
    can_assign_help: Mapped[bool] = mapped_column(Boolean, default=False)
    can_change_status: Mapped[bool] = mapped_column(Boolean, default=False)
    can_make_roles: Mapped[bool] = mapped_column(Boolean, default=False)
    can_change_roles: Mapped[bool] = mapped_column(Boolean, default=False)
    can_assign_people_to_project: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(
        "Project", back_populates="roles", foreign_keys=[project_id], lazy="selectin"
    )
    user_projects: Mapped[list[UserProject]] = relationship(
        "UserProject", back_populates="role", lazy="selectin"
    )
