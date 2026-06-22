# SecureIncident — Operational Guides

Practical, verified guides for working on SecureIncident. Every command in these
guides was run against the repository before being documented.

> **Canonical branch:** CI/CD, pre-commit, and lint/security tooling are described
> as they exist on **`main`** (the integration target), which carries the full
> workflow set. Feature branches (e.g. `docs_dev`) may lag; per-guide notes call
> out where they differ.

| Guide | What it covers |
|-------|----------------|
| [Running the application](./running-the-app.md) | Docker Compose, manual dev setup, per-service builds, environment variables, service URLs |
| [Testing](./testing.md) | Backend `pytest` suite, frontend lint/build checks, what CI runs |
| [Pre-commit hooks](./pre-commit.md) | Installing and running the hooks, what each one does, known caveats |
| [CI/CD](./ci-cd.md) | GitHub Actions pipelines, triggers, GHCR images, EC2 deployment |
| [Pull requests](./pull-requests.md) | Branch naming, commit style, the pre-PR checklist |

## TL;DR

```bash
# Run the whole stack (PostgreSQL + backend + frontend + Mailpit) on http://localhost
make up

# Run the backend test suite (DB container must be up)
cd backend && uv run pytest

# Frontend checks
cd Frontend && npm run lint && npm run build

# Install the git hooks once per clone
pre-commit install
```

## Repository layout

```
SecureIncident/
├── Frontend/                  # React 19 + TypeScript + Vite + Tailwind CSS 4
├── backend/                   # FastAPI + SQLAlchemy + Alembic (Python 3.14)
├── docs/
│   ├── guides/                # ← these operational guides
│   └── api/                   # OpenAPI specification
├── .github/workflows/         # backend-ci.yml, frontend-ci.yml
├── .pre-commit-config.yaml
├── Makefile                   # local + production compose shortcuts
├── docker-compose.local.yml   # local development stack
├── docker-compose.yml         # production stack (pulls GHCR images)
└── pyproject.toml             # backend deps (uv) + ruff/vulture config
```

> The files `docs/documentation.md`, `docs/backend.md`, `docs/frontend.md` and
> `docs/tests.md` belong to a separate pandoc PDF build (`docs/main.py` →
> `dokumentacja.pdf`). They are **not** part of these guides — leave them alone.
