from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Organization(Base):
    __tablename__ = "organization"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    org_owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    join_code = Column(String(20), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_organizations", foreign_keys=[org_owner_id])
    users = relationship("User", back_populates="organization", foreign_keys="User.organization_id")
    projects = relationship("Project", back_populates="organization", cascade="all, delete-orphan")
