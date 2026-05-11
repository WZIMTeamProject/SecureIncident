# Database Queries (SQLAlchemy 2.0 Async)

## Session Usage

Use the async session via dependency injection in every route. Never create sessions manually inside route handlers.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.dependencies.db import get_db

@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentResponse:
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentResponse.model_validate(incident)
```

## Select Patterns

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

# Single row — use scalar_one_or_none(), handle None explicitly
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()

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

## Write Operations

```python
# Create
incident = Incident(**body.model_dump(), reporter_id=current_user.id)
db.add(incident)
await db.commit()
await db.refresh(incident)

# Update
incident.status = new_status
incident.updated_at = datetime.utcnow()
await db.commit()

# Delete
await db.delete(incident)
await db.commit()
```

## Transactions

FastAPI's request lifecycle manages one session per request. Each `await db.commit()` commits the transaction. If you need to perform multiple writes atomically, do them before a single `commit()`. On error, SQLAlchemy rolls back automatically when the session context exits.

## Parameterized Queries

Never interpolate user input into SQL strings. SQLAlchemy's ORM and `text()` with `bindparam` are always safe:

```python
# Safe
await db.execute(select(User).where(User.email == email))

# Also safe (raw SQL with bound params)
from sqlalchemy import text
await db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```
