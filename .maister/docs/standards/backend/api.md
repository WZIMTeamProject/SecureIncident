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
| `POST` | Create a new resource |
| `PUT` | Full replacement of a resource |
| `PATCH` | Partial update |
| `DELETE` | Remove a resource |

## Response Status Codes

```python
# Creation
return JSONResponse(status_code=status.HTTP_201_CREATED, content=response.model_dump())

# No content (delete, assign)
return Response(status_code=status.HTTP_204_NO_CONTENT)

# Common client errors
raise HTTPException(status_code=400, detail="Invalid request")
raise HTTPException(status_code=401, detail="Not authenticated")
raise HTTPException(status_code=403, detail="Insufficient permissions")
raise HTTPException(status_code=404, detail="Incident not found")
raise HTTPException(status_code=409, detail="Email already registered")
```

## Request / Response Schemas

Every endpoint has explicit Pydantic `request_model` and `response_model`. Never return raw SQLAlchemy model instances.

```python
@router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(
    body: CreateIncidentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IncidentResponse:
```

## Authentication & Authorization

- Every endpoint except `POST /auth/register` and `POST /auth/login` requires authentication
- Always inject `current_user` via `Depends(get_current_user)` — never read the JWT manually in a route
- After confirming identity, check project membership and role permissions explicitly
- Authorization check order: authenticate → load resource → verify ownership/membership → execute

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
