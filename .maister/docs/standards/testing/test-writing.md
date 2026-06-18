# Test Writing

## Guiding Principles

- **Test behavior, not implementation** — tests should survive refactoring. Test what the code does, not which internal functions it calls.
- **One assertion per test is a guideline, not a law** — related assertions about the same behavior can live in one test. Unrelated behaviors belong in separate tests.
- **Tests are documentation** — a failing test should tell you exactly what broke and why.

## Naming

Group tests into classes named `Test<Feature>`. Individual methods follow `test_<scenario>_<expected_result>`. All test methods are `async def`. Use `assert` statements — not `self.assert*`.

```python
class TestLogin:
    async def test_login_returns_200_with_valid_credentials(self, client, test_user): ...
    async def test_login_returns_401_with_wrong_password(self, client, test_user): ...
    async def test_login_returns_422_when_username_missing(self, client): ...

class TestCreateIncident:
    async def test_create_incident_returns_201_with_valid_data(self, client, auth_headers, test_project): ...
    async def test_create_incident_returns_403_when_user_not_project_member(self, client, auth_headers): ...
```

## FastAPI Integration Tests (pytest + httpx)

Use `pytest-asyncio` (auto mode — no `@pytest.mark.asyncio` decorator needed) with an `AsyncClient` that hits the actual FastAPI app and a real test database. Do not mock the database.

```python
async def test_create_incident_returns_201(self, client: AsyncClient, auth_headers: dict):
    payload = {"title": "Login broken", "description": "Users cannot log in", "category_id": "..."}
    response = await client.post("/api/incidents", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert "id" in response.json()
```

## Fixtures — flush() and Savepoints

All fixtures that insert data call `db.add(obj)` + `await db.flush()` — **never** `await db.commit()`. The `db` fixture wraps each test in a savepoint that rolls back after the test, keeping tests isolated without truncating tables:

```python
@pytest.fixture(scope="function")
async def test_user(db: AsyncSession) -> User:
    user = User(username="testuser", ...)
    db.add(user)
    await db.flush()   # Makes user visible within the transaction; rolled back after test
    return user

# db fixture (in conftest.py) uses join_transaction_mode='create_savepoint'
# and calls await transaction.rollback() in teardown
```

All db-touching fixtures have `scope='function'` and use `yield` (not `return`) so teardown runs.

## Auth Headers Fixture

Authentication for test HTTP requests always uses a fixture returning `{'Authorization': 'Bearer <token>'}`:

```python
@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}
```

Test methods accept the fixture and pass it to the HTTP client:

```python
response = await client.post("/api/projects", headers=auth_headers, json={...})
```

## Test Organization

```
tests/
  conftest.py          # shared fixtures: db session, test client, auth tokens
  test_auth.py         # /auth endpoints
  test_incidents.py    # /incidents endpoints
  test_projects.py     # /projects endpoints
```

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
