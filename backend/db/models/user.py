import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_organization_id", "organization_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    bio: Mapped[str | None] = mapped_column(String(1000), nullable=True, default=None)
    profile_picture_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    organization: Mapped[Organization | None] = relationship(
        "Organization",
        back_populates="users",
        foreign_keys=[organization_id],
        lazy="selectin",
    )
    owned_organizations: Mapped[list[Organization]] = relationship(
        "Organization",
        back_populates="owner",
        foreign_keys="Organization.org_owner_id",
        lazy="selectin",
    )
    owned_projects: Mapped[list[Project]] = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.project_owner_id",
        lazy="selectin",
    )
    user_projects: Mapped[list[UserProject]] = relationship(
        "UserProject",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    incidents: Mapped[list[Incident]] = relationship(
        "Incident",
        back_populates="reporter",
        foreign_keys="Incident.reporter_id",
        lazy="selectin",
    )
    assigned_incidents: Mapped[list[Incident]] = relationship(
        "Incident",
        back_populates="primary_assignee",
        foreign_keys="Incident.primary_assignee_id",
        lazy="selectin",
    )
    incident_logs: Mapped[list[IncidentLog]] = relationship(
        "IncidentLog", back_populates="person", lazy="selectin"
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="author", lazy="selectin"
    )
    created_invites: Mapped[list[OrganizationInvite]] = relationship(
        "OrganizationInvite",
        back_populates="created_by",
        foreign_keys="OrganizationInvite.created_by_id",
        lazy="selectin",
    )
    incident_helpers: Mapped[list[IncidentHelper]] = relationship(
        "IncidentHelper", back_populates="user", lazy="selectin"
    )
