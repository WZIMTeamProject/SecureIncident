from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_org_owner_id", "org_owner_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    join_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship(
        "User", back_populates="owned_organizations", foreign_keys=[org_owner_id], lazy="selectin"
    )
    users: Mapped[List["User"]] = relationship(
        "User", back_populates="organization", foreign_keys="User.organization_id", lazy="selectin"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="organization", cascade="all, delete-orphan", lazy="selectin"
    )
    organization_invites: Mapped[List["OrganizationInvite"]] = relationship(
        "OrganizationInvite", back_populates="organization", lazy="selectin"
    )
