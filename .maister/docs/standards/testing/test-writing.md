# Test Writing

## Guiding Principles

- **Test behavior, not implementation** — tests should survive refactoring. Test what the code does, not which internal functions it calls.
- **One assertion per test is a guideline, not a law** — related assertions about the same behavior can live in one test. Unrelated behaviors belong in separate tests.
- **Tests are documentation** — a failing test should tell you exactly what broke and why.

## Naming

Use descriptive names that read as a sentence: `test_<scenario>_<expected_result>`.

```python
# Good
def test_create_incident_returns_201_with_valid_data(): ...
def test_create_incident_returns_403_when_user_not_project_member(): ...
def test_get_incident_returns_404_when_not_found(): ...

# Bad
def test_incident(): ...
def test_create(): ...
```

## FastAPI Integration Tests (pytest + httpx)

Use `pytest-asyncio` with an `AsyncClient` that hits the actual FastAPI app and a test database. Don't mock the database for integration tests — use a separate test database or SQLite in-memory.

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_incident_returns_201(client: AsyncClient, auth_headers: dict):
    payload = {"title": "Login broken", "description": "Users cannot log in", "category_id": 1}
    response = await client.post("/api/incidents", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Login broken"
    assert "id" in data
```

## Test Organization

```
tests/
  conftest.py          # shared fixtures: db session, test client, auth tokens
  test_auth.py         # /auth endpoints
  test_incidents.py    # /incidents endpoints
  test_projects.py     # /projects endpoints
```

## Fixtures

Define reusable fixtures in `conftest.py`. A minimal set:
- `db` — async session connected to a test database
- `client` — `AsyncClient` wrapping the FastAPI app
- `test_user` — a created user record
- `auth_headers` — `{"Authorization": "Bearer <token>"}` for the test user
- `test_project` — a project the test user is a member of

## What to Test

- **Happy path**: valid input → expected response + status code
- **Auth**: unauthenticated request → 401; unauthorized (wrong project) → 403
- **Validation**: missing required field → 422; invalid format → 422
- **Not found**: valid ID that doesn't exist → 404
- **Business rules**: violated constraint (e.g., duplicate email) → 409

## What Not to Test

- Framework behavior (FastAPI's validation is already tested by Pydantic)
- Trivial getters/setters with no logic
- Third-party library internals
