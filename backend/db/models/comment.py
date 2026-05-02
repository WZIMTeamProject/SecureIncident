from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incident.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    incident = relationship("Incident", back_populates="comments", foreign_keys=[incident_id])
    user = relationship("User", back_populates="comments", foreign_keys=[user_id])
