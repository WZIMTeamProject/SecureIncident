from datetime import datetime
from sqlalchemy import Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        Index("ix_comments_incident_id", "incident_id"),
        Index("ix_comments_author_id", "author_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    incident: Mapped["Incident"] = relationship(
        "Incident", back_populates="comments", foreign_keys=[incident_id], lazy="selectin"
    )
    author: Mapped["User"] = relationship(
        "User", back_populates="comments", foreign_keys=[author_id], lazy="selectin"
    )
