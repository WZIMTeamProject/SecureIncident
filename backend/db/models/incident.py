from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid


class IncidentStatus(str, PyEnum):
    NEW = "NEW"
    PROBLEM_IS_BEING_SOLVED = "PROBLEM_IS_BEING_SOLVED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class IncidentPriority(str, PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Incident(Base):
    __tablename__ = "incident"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    helper_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    title = Column(String(200), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.NEW, nullable=False)
    priority = Column(Enum(IncidentPriority), default=IncidentPriority.LOW, nullable=False)
    description = Column(Text, nullable=False)
    creation_date = Column(DateTime, server_default=func.now())
    closing_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    reporter = relationship("User", back_populates="incidents", foreign_keys=[user_id])
    helper = relationship("User", back_populates="assigned_incidents", foreign_keys=[helper_id])
    project = relationship("Project", back_populates="incidents", foreign_keys=[project_id])
    comments = relationship("Comment", back_populates="incident", cascade="all, delete-orphan")
    logs = relationship("IncidentLog", back_populates="incident", cascade="all, delete-orphan")
    categories = relationship(
        "Category",
        secondary="incident_category",
        back_populates="incidents",
    )
