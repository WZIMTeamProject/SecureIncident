from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Comment(Base):
    __tablename__ = "comment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incident.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    incident = relationship("Incident", back_populates="comments", foreign_keys=[incident_id])
    user = relationship("User", back_populates="comments", foreign_keys=[user_id])
