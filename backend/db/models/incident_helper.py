import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base


class IncidentHelper(Base):
    __tablename__ = "incident_helpers"
    __table_args__ = (
        Index("ix_incident_helpers_incident_id", "incident_id"),
        Index("ix_incident_helpers_user_id", "user_id"),
    )

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    incident: Mapped[Incident] = relationship(
        "Incident", back_populates="helpers", lazy="selectin"
    )
    user: Mapped[User] = relationship(
        "User", back_populates="incident_helpers", lazy="selectin"
    )
