# API Design (FastAPI)

## URL Structure

- Resources are **plural nouns**: `/projects`, `/incidents`, `/users`
- Use URL path for resource identity: `GET /incidents/{incident_id}`
- Nest to express ownership, max 2 levels: `GET /projects/{project_id}/incidents`
- Use query parameters for filtering, sorting, pagination: `GET /incidents?status=open&page=1&limit=20`
- All routes mount under `/api` prefix (already configured in `main.py`)

## HTTP Methods

| Method | Use |
|--------|-----|
| `GET` | Read resource(s), never mutates state |
| `POST` | Create a new resource — returns 201 + `CreatedIdResponse` |
| `PATCH` | Partial update — returns 204 No Content |
| `DELETE` | Remove a resource — returns 204 No Content |

## Response Status Codes

```python
# Creation — always 201 + CreatedIdResponse
return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": str(obj.id)})

# No content (update, delete, action endpoints)
return Response(status_code=status.HTTP_204_NO_CONTENT)

# Common client errors
raise HTTPException(status_code=400, detail="Invalid request")
raise HTTPException(status_code=401, detail="Not authenticated")
raise HTTPException(status_code=403, detail="Insufficient permissions")
raise HTTPException(status_code=404, detail="Incident not found")
raise HTTPException(status_code=409, detail="Email already registered")
```

## Schema Organization

Pydantic schemas are organized by domain under `api/schemas/<domain>/` with separate files:

```
api/schemas/
  incident/
    request.py    # CreateIncidentRequest, UpdateIncidentStatusRequest, ...
    response.py   # IncidentListResponse, IncidentDetailsResponse, ...
  project/
    request.py
    response.py
  common/
    base.py       # CreatedIdResponse, ErrorResponse
    pagination.py # PaginatedResponse[T]
    enums.py
```

No monolithic schema files. Every endpoint has explicit Pydantic `request_model` and `response_model` — never return raw SQLAlchemy model instances.

## Route Handler Structure

Route handlers contain **zero business logic**. They only extract parameters, call a service function, and return the result:

```python
@router.post(
    "/projects/{project_id}/incidents",
    response_model=CreatedIdResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    project_id: UUID,
    body: CreateIncidentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CreatedIdResponse:
    return await incident_service.create_incident(db, project_id, body, current_user)
```

All validation, authorization, and DB access happen in the service layer. Services are imported as modules (`from api.services import incident_service`), never instantiated.

## Authentication & Authorization

- Every endpoint except `POST /auth/register` and `POST /auth/login` requires authentication
- Always inject `current_user` via `Depends(get_current_user)` — never read the JWT manually in a route
- After confirming identity, check project membership and role permissions explicitly
- Authorization check order: authenticate → load resource → verify ownership/membership → execute

## Authorization Guard Helpers

Extract 404/403 guard logic into private async helper functions in the service file:

```python
async def _get_incident_or_404(db: AsyncSession, incident_id: UUID) -> Incident:
    incident = await repositories.incident_repo.get_by_id(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

async def _get_membership_or_403(db: AsyncSession, project_id: UUID, user_id: UUID) -> UserProject:
    membership = await repositories.project_repo.get_membership(db, project_id, user_id)
    if membership is None:
        raise HTTPException(status_code=403, detail="Not a project member")
    return membership
```

## Pagination

All list endpoints return paginated results with a consistent envelope:

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    has_more: bool
```

Default limit: 20. Maximum limit: 100.

## Error Response Format

Stick to FastAPI's default validation error format (422) for schema errors. For application errors use:

```json
{"detail": "Human-readable error message"}
```
