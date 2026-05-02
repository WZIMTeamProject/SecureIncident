from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from enum import Enum as PyEnum


class IncidentStatus(PyEnum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class Incident(Base):
    __tablename__ = "incident"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    helper_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    title = Column(String(200), nullable=False)
    status = Column(String(50), default="Open", nullable=False)
    priority_level = Column(Integer, default=1, nullable=False)
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
