from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    name = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[project_owner_id])
    organization = relationship("Organization", back_populates="projects", foreign_keys=[organization_id])
    user_projects = relationship("UserProject", back_populates="project", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="project", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="project", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="project", cascade="all, delete-orphan")
