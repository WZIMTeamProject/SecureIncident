from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project.id"), nullable=False)
    name = Column(String(50), nullable=False)
    can_write_tickets = Column(Boolean, default=False)
    can_help = Column(Boolean, default=False)
    can_assign_help = Column(Boolean, default=False)
    can_change_status = Column(Boolean, default=False)
    can_make_roles = Column(Boolean, default=False)
    can_change_roles = Column(Boolean, default=False)
    can_assign_people_to_project = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="roles", foreign_keys=[project_id])
    user_projects = relationship("UserProject", back_populates="role")
