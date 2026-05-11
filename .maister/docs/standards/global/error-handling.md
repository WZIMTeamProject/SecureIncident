# Error Handling

## Core Principle
Handle errors at system boundaries (user input, external APIs, DB calls). Trust internal code and framework guarantees — don't wrap every internal function in try/catch.

## FastAPI (Backend)

### HTTP Exceptions
Use `HTTPException` for client errors; let FastAPI's default handler convert unhandled exceptions to 500s.

```python
from fastapi import HTTPException, status

# Correct: specific status code and message
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
```

### Custom Exception Handlers
Register a global handler in `main.py` for domain-specific exceptions instead of scattering try/except.

### Never Expose Internals
Do not return stack traces, SQL errors, or internal paths in API responses. Log the full error server-side; return a generic message to the client.

### Database Errors
Catch `SQLAlchemyError` at the service/route layer. Roll back the session and raise an appropriate `HTTPException`.

## React / TypeScript (Frontend)

### API Call Errors
Handle errors where data is fetched — in the hook or service function, not in components. Return a typed result: `{ data, error }` or use React Query's error state.

### User-Facing Messages
Show actionable messages: "Failed to create incident. Please try again." — not raw error strings from the server.

### Never Silently Swallow Errors
An empty `catch {}` block is always wrong. At minimum, log to console in development and show feedback to the user.

### Form Validation Errors
Display field-level errors next to the relevant input. Map server 422 validation errors to form fields.

## General Rules

- **Fail fast**: validate at entry points before executing business logic
- **Specific over generic**: `IncidentNotFoundError` is better than `ValueError`
- **Log with context**: include relevant IDs and operation names in error logs
- **No sensitive data in logs**: never log passwords, tokens, or full request bodies
