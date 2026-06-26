# Testing

## Backend — `pytest`

The backend has an integration test suite (**261 tests** as of this writing)
that runs against a **real PostgreSQL database** via `httpx.AsyncClient` against
the actual FastAPI app. There is no DB mocking — each test runs inside a
transaction that is rolled back afterwards, so no data persists between tests.

### Prerequisites

The database container must be running:

```bash
docker compose -f docker-compose.local.yml up -d db
```

The suite needs `DATABASE_URL` and a `SECRET_KEY` in the environment (or in the
repo-root `.env`). `backend/pytest.ini` enables asyncio auto mode and sets
`pythonpath = .`, so no decorator is needed on async tests.

### Run the suite (from `backend/`)

```bash
# With uv (recommended) — runs inside the managed .venv:
uv run pytest

# Without uv — activate the virtualenv first:
source ../.venv/bin/activate    # macOS/Linux
# ..\.venv\Scripts\activate     # Windows
pytest
```

If `DATABASE_URL`/`SECRET_KEY` are not already exported, pass them inline:

```bash
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/secure_incident" \
SECRET_KEY="test-secret" \
uv run pytest
```

### Useful invocations

```bash
uv run pytest -q                       # quiet summary
uv run pytest tests/test_profiles.py -v  # one file, verbose
uv run pytest -k password_reset        # match by test name
```

### Conventions

Tests live in `backend/tests/`, grouped into `Test<Feature>` classes with
`test_<scenario>_<expected_result>` method names. Fixtures use
`db.add()` + `await db.flush()` (never `commit`) inside savepoint-wrapped
transactions. The coverage matrix per endpoint: happy path, 401, 403, 422, 404,
and business-rule (409) cases. See
`.maister/docs/standards/testing/test-writing.md` for the full standard.

---

## Frontend — lint & build

The frontend has **no unit-test runner**; its CI-equivalent checks are linting
and a type-checked production build.

```bash
cd Frontend

npm run lint     # ESLint over the whole project
npm run build    # tsc -b (type-check) + vite build
```

`npm run build` runs the TypeScript compiler first (`tsc -b`), so a type error
fails the build — this doubles as the type-check gate. A clean run produces the
`dist/` bundle.

> Three pre-existing ESLint **warnings** come from generated files under
> `src/api/**/index.ts`. They are warnings, not errors, and do not fail the lint
> step or CI.

---

## What CI runs

On the `main` branch (the canonical setup), tests and checks run on **both**
feature-branch pushes / PRs and on merge to `main`:

- **`backend-qa.yml`** (branches + PRs) runs `pytest` against a `postgres:16`
  service — but pins **Python 3.12**, which differs from the 3.14 used for the
  production deploy. It also runs the `bandit` / `pip-audit` / `vulture` security
  scanners.
- **`backend-ci.yml`** (push to `main`) runs `uv run pytest` on **Python 3.14**
  before building and deploying the image — failing tests block the deploy.
- **`frontend-qa.yml`** (branches + PRs) runs `npm ci` + `npm audit --audit-level=high`
  and a dry-run Docker build. Neither QA nor the deploy pipeline runs
  `npm run lint` — **linting is a local / pre-commit responsibility only.**

See [CI/CD](./ci-cd.md) for the full pipeline breakdown. Run these checks locally
before opening a PR (see [Pull requests](./pull-requests.md)).

> **Branch note:** older branches (e.g. `docs_dev`) have a smaller workflow set
> that only triggers on push to `main`. The description above reflects `main`.
