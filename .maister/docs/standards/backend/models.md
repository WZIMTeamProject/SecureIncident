# SQLAlchemy Models

## Model Definition Pattern

Use SQLAlchemy 2.0 declarative style with `DeclarativeBase` and typed columns:

```python
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base
import datetime
import uuid

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    reporter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="incidents")
    reporter: Mapped["User"] = relationship("User", foreign_keys=[reporter_id])
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="incident", cascade="all, delete-orphan")
```

## Naming

- Model class: `PascalCase` singular (`Incident`, `Project`, `User`)
- Table name: `snake_case` plural (`incidents`, `projects`, `users`)
- Column names: `snake_case`
- Foreign key columns: `<related_model>_id` (`project_id`, `reporter_id`)

## Required Fields on Every Model

- `id` — UUID primary key with `default=uuid.uuid4`
- `created_at` — server-side default timestamp
- `updated_at` — server-side default + `onupdate` timestamp

## Database Constraints

Enforce data integrity at the database level, not just application level:
- `nullable=False` for required fields
- `unique=True` for fields like email, usernames
- `ForeignKey` with appropriate `ondelete` behavior (`CASCADE`, `SET NULL`, or `RESTRICT`)
- Use `CheckConstraint` for enum-like string columns or value ranges

## Indexes

```python
from sqlalchemy import Index

class Incident(Base):
    __tablename__ = "incidents"
    # ...
    __table_args__ = (
        Index("ix_incidents_project_id", "project_id"),
        Index("ix_incidents_reporter_id", "reporter_id"),
        Index("ix_incidents_status", "status"),
    )
```

Index all foreign key columns and columns used in frequent `WHERE` clauses.

## Relationships

- Define `back_populates` on both sides of every relationship
- Specify `cascade="all, delete-orphan"` for owned child relationships (comments belong to incident)
- Use `lazy="selectin"` in async contexts to avoid lazy-loading errors; or use explicit `joinedload` in queries
