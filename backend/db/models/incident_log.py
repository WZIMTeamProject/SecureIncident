from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from enum import Enum


class LogType(Enum):
    PRIORITY_CHANGE = "priority_change"
    COMMENT = "comment"
    HELPER_ADDED = "helper_added"
    HELPER_REMOVED = "helper_removed"
    STATUS_CHANGE = "status_change"
    CREATED = "created"
    CLOSED = "closed"


class IncidentLog(Base):
    __tablename__ = "incident_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incident.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    type = Column(String(50), nullable=False)
    comment = Column(Text, nullable=False)
    date = Column(DateTime, server_default=func.now())

    # Relationships
    incident = relationship("Incident", back_populates="logs", foreign_keys=[incident_id])
    person = relationship("User", back_populates="incident_logs", foreign_keys=[person_id])
