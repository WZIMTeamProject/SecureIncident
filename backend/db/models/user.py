from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    login = Column(String(50), nullable=False, unique=True, index=True)
    mail = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="users", foreign_keys=[organization_id])
    owned_organizations = relationship("Organization", back_populates="owner", foreign_keys="Organization.org_owner_id")
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.project_owner_id")
    user_projects = relationship("UserProject", back_populates="user", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="reporter", foreign_keys="Incident.user_id")
    assigned_incidents = relationship("Incident", back_populates="helper", foreign_keys="Incident.helper_id")
    incident_logs = relationship("IncidentLog", back_populates="person")
    comments = relationship("Comment", back_populates="user")
