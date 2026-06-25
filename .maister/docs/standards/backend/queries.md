# Database Queries (SQLAlchemy 2.0 Async)

## Session Usage

Use the async session via dependency injection in every route. Never create sessions manually inside route handlers.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies.db import get_db

@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentResponse:
    return await incident_service.get_incident(db, incident_id, current_user)
```

## Repository Pattern

Services never issue SQLAlchemy queries directly. All database access goes through module-level functions in `db/repositories/<model>_repo.py`:

```python
# In service layer
from db import repositories

incident = await repositories.incident_repo.get_by_id(db, incident_id)
await repositories.incident_repo.create(db, incident)
```

Repository files follow the naming pattern `<model>_repo.py` (e.g., `incident_repo.py`, `user_repo.py`). Repository functions return ORM model instances or `None` — never raw query result proxies.

## flush() vs commit() Split

**Repositories** call `db.add()` + `await db.flush()` — they do NOT commit:

```python
# In repository (incident_repo.py)
async def create(db: AsyncSession, incident: Incident) -> Incident:
    db.add(incident)
    await db.flush()
    return incident
```

**Services** call `await db.commit()` (and optionally `await db.refresh()`) after all repository calls:

```python
# In service layer
inc = Incident(**body.model_dump(), reporter_id=current_user.id)
await repositories.incident_repo.create(db, inc)
await db.commit()
await db.refresh(inc)
```

This pattern ensures atomicity: a service function can call multiple repos before the single commit.

## Select Patterns

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

# Single row — use scalar_one_or_none(), handle None explicitly
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()

# COUNT queries — scalar_one() since result is always present
total = (await db.execute(count_stmt)).scalar_one()

# Multiple rows
result = await db.execute(select(Incident).where(Incident.project_id == project_id))
incidents = result.scalars().all()

# Eager-load relationships to avoid N+1
result = await db.execute(
    select(Incident)
    .where(Incident.project_id == project_id)
    .options(selectinload(Incident.comments), selectinload(Incident.reporter))
)
```

## Avoiding N+1 Queries

**Never** access a relationship attribute in a loop without eager loading it first. Use `selectinload` (separate IN query) or `joinedload` (JOIN) when you know you'll access related data.

```python
# Wrong — triggers N queries for N incidents
incidents = (await db.execute(select(Incident))).scalars().all()
for incident in incidents:
    print(incident.reporter.name)  # N+1!

# Correct — 2 queries total
incidents = (await db.execute(
    select(Incident).options(selectinload(Incident.reporter))
)).scalars().all()
```

## SQL None / Boolean Comparisons in Repositories

In repository query filters, use `== None` / `== True` (**not** `is None` / `is True`) for SQLAlchemy column comparisons. `is None` short-circuits to a plain Python `bool` instead of building a SQL expression, so the filter would be wrong.

```python
# Correct — builds `WHERE incidents.closing_date IS NULL`
select(Incident).where(Incident.closing_date == None)

# Wrong — evaluates to a Python bool, not a SQL expression
select(Incident).where(Incident.closing_date is None)
```

This is why repository files carry per-file Ruff ignores for `E711`/`E712`:

```toml
# pyproject.toml
[tool.ruff.lint.per-file-ignores]
"backend/db/repositories/*.py" = ["E711", "E712"]
```

## Parameterized Queries

Never interpolate user input into SQL strings. SQLAlchemy's ORM and `text()` with `bindparam` are always safe:

```python
# Safe
await db.execute(select(User).where(User.email == email))

# Also safe (raw SQL with bound params)
from sqlalchemy import text
await db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```
