from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    name = Column(String(50), nullable=False)
    can_write_tickets = Column(Boolean, default=False)
    can_help = Column(Boolean, default=False)
    can_assign_help = Column(Boolean, default=False)
    can_make_roles = Column(Boolean, default=False)
    can_change_roles = Column(Boolean, default=False)
    can_assign_people_to_project = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="roles", foreign_keys=[project_id])
    user_projects = relationship("UserProject", back_populates="role")
