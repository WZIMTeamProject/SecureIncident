from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserProject(Base):
    __tablename__ = "user_projects"
    __table_args__ = (
        Index("ix_user_projects_role_id", "role_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="user_projects", foreign_keys=[user_id], lazy="selectin"
    )
    project: Mapped["Project"] = relationship(
        "Project", back_populates="user_projects", foreign_keys=[project_id], lazy="selectin"
    )
    role: Mapped["Role"] = relationship(
        "Role", back_populates="user_projects", foreign_keys=[role_id], lazy="selectin"
    )
