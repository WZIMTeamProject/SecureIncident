from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid


class LogType(str, PyEnum):
    PRIORITY_CHANGE = "priority_change"
    COMMENT = "comment"
    HELPER_ADDED = "helper_added"
    HELPER_REMOVED = "helper_removed"
    STATUS_CHANGE = "status_change"
    CREATED = "created"
    CLOSED = "closed"


class IncidentLog(Base):
    __tablename__ = "incident_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incident.id"), nullable=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    type = Column(Enum(LogType), nullable=False)
    comment = Column(Text, nullable=True)
    date = Column(DateTime, server_default=func.now())

    # Relationships
    incident = relationship("Incident", back_populates="logs", foreign_keys=[incident_id])
    person = relationship("User", back_populates="incident_logs", foreign_keys=[person_id])
