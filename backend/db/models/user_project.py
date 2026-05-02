from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class UserProject(Base):
    __tablename__ = "user_project"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_projects", foreign_keys=[user_id])
    project = relationship("Project", back_populates="user_projects", foreign_keys=[project_id])
    role = relationship("Role", back_populates="user_projects", foreign_keys=[role_id])
