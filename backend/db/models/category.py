from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.base import Base


# Association table for many-to-many relationship between helper and category
helper_category = Table(
    "helper_category",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("project.id"), primary_key=True),
    Column("helper_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True),
)

# Association table for many-to-many relationship between incident and category
incident_category = Table(
    "incident_category",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="categories", foreign_keys=[project_id])
    incidents = relationship(
        "Incident",
        secondary=incident_category,
        back_populates="categories",
    )
