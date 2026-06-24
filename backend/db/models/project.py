import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_project_owner_id", "project_owner_id"),
        Index("ix_projects_organization_id", "organization_id"),
        Index("ix_projects_scope", "scope"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped[User] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[project_owner_id],
        lazy="selectin",
    )
    organization: Mapped[Organization | None] = relationship(
        "Organization",
        back_populates="projects",
        foreign_keys=[organization_id],
        lazy="selectin",
    )
    user_projects: Mapped[list[UserProject]] = relationship(
        "UserProject",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    roles: Mapped[list[Role]] = relationship(
        "Role", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    incidents: Mapped[list[Incident]] = relationship(
        "Incident",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    categories: Mapped[list[Category]] = relationship(
        "Category",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    invites: Mapped[list[OrganizationInvite]] = relationship(
        "OrganizationInvite", back_populates="project", lazy="selectin"
    )
