from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_project_owner_id", "project_owner_id"),
        Index("ix_projects_organization_id", "organization_id"),
        Index("ix_projects_scope", "scope"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship(
        "User", back_populates="owned_projects", foreign_keys=[project_owner_id], lazy="selectin"
    )
    organization: Mapped[Optional["Organization"]] = relationship(
        "Organization", back_populates="projects", foreign_keys=[organization_id], lazy="selectin"
    )
    user_projects: Mapped[List["UserProject"]] = relationship(
        "UserProject", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    incidents: Mapped[List["Incident"]] = relationship(
        "Incident", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    categories: Mapped[List["Category"]] = relationship(
        "Category", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
