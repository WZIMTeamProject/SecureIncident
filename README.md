# SecureIncident

**A web-based incident reporting platform for managing, tracking, and resolving
internal incidents with a full audit trail.**

SecureIncident gives organizations a single place to report problems, route them
to the right project, work them through a defined lifecycle, and keep an
immutable record of who did what and when. It is built as a React single-page
app talking to a FastAPI REST backend over an OpenAPI-defined contract, backed
by PostgreSQL.

---

## What it does

- **Incident lifecycle** — report an incident (title, description, category,
  project are mandatory), discuss it through comments, assign a solver, and move
  it through statuses to resolution or closure. Incidents are never deleted from
  the UI — only resolved or closed — so history stays intact.
- **Organizations, projects & roles** — incidents belong to exactly one project;
  projects belong to an organization. Each user has exactly one role per project
  (roles are project-scoped, not global), enforced server-side for every action.
- **Immutable audit trail** — comment additions, status changes, solver changes,
  logins, and admin operations are recorded in an append-only audit log that the
  UI cannot edit.
- **Authentication & account recovery** — JWT-based auth (PyJWT), bcrypt password
  hashing, and a password-reset-by-email flow with expiring single-use tokens.
- **Comments are immutable** — to correct an earlier comment a user adds a new
  one, preserving the conversation history.

> A fuller product description lives in
> [`Specyfikacja_Secure_Incident.md`](./Specyfikacja_Secure_Incident.md).

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript (strict), React Router 7, Vite 8, Tailwind CSS 4 |
| Backend | FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0, Alembic (Python 3.14) |
| Database | PostgreSQL 16 (async via `asyncpg`) |
| Auth | PyJWT, bcrypt (passlib) |
| Tooling | uv + `pyproject.toml`, ruff, vulture, bandit, pip-audit, ESLint, pre-commit |
| Infra | Docker + Docker Compose, GitHub Actions (build + QA on PRs, deploy on `main`) → GHCR → AWS EC2 + RDS |
| Local email | Mailpit (SMTP sink) |

---

## Architecture

```
                         ┌──────────────────────────┐
  Browser  ──HTTPS──▶    │  Frontend (nginx)         │   React SPA, static build
                         │  proxies /api/ ──────────────┐
                         └──────────────────────────┘   │
                                                         ▼
                         ┌──────────────────────────┐
                         │  Backend (FastAPI)        │   JWT auth + RBAC
                         │  routes → services → repos│   business rules
                         └─────────────┬────────────┘
                                       │ SQLAlchemy (async)
                                       ▼
                         ┌──────────────────────────┐
                         │  PostgreSQL               │
                         └──────────────────────────┘
```

Domain hierarchy: **Organization → Projects → Incidents**, with `User` and
`UserProject` (one role per user per project) associations. The backend is
layered — route handlers delegate to services, services call repositories, and
all database access goes through the async session. See the OpenAPI spec under
[`docs/api/`](./docs/api/).

### Repository layout

```
SecureIncident/
├── Frontend/                  # React 19 + TypeScript + Vite + Tailwind CSS 4
├── backend/                   # FastAPI + SQLAlchemy + Alembic
│   ├── api/                   # routes, schemas, dependencies
│   ├── db/                    # models, repositories, migrations (alembic/)
│   ├── services/              # business logic
│   └── tests/                 # pytest integration suite
├── docs/
│   ├── guides/                # operational guides (start here ↓)
│   └── api/                   # OpenAPI specification
├── .github/workflows/         # backend-ci.yml, frontend-ci.yml
├── docker-compose.local.yml   # local development stack
├── docker-compose.yml         # production stack (GHCR images)
├── Makefile                   # compose shortcuts
└── pyproject.toml             # backend deps + ruff/vulture config
```

---

## Quick start

Run the full stack (PostgreSQL + backend + frontend + Mailpit) in containers:

```bash
make up          # = docker compose -f docker-compose.local.yml up --build
```

Then open **http://localhost** (app) and **http://localhost:8025** (Mailpit).
Stop with `make down`.

Prefer hot-reload development? Run the database in Docker and the services from
source — see the guide below.

---

## Documentation

Practical, **verified** guides live in [`docs/guides/`](./docs/guides/README.md):

| Guide | Covers |
|-------|--------|
| [Running the application](./docs/guides/running-the-app.md) | Docker Compose, manual dev, per-service builds, env vars, URLs |
| [Testing](./docs/guides/testing.md) | Backend `pytest`, frontend lint/build, what CI runs |
| [Pre-commit hooks](./docs/guides/pre-commit.md) | Installing/running hooks, what each does, caveats |
| [CI/CD](./docs/guides/ci-cd.md) | GitHub Actions pipelines, GHCR, EC2 deploy |
| [Pull requests](./docs/guides/pull-requests.md) | Branch naming, commit style, pre-PR checklist |

---

## Project status

Early-stage MVP under active development toward a working end-to-end incident
lifecycle. Coding standards and architecture decisions are tracked in
`.maister/docs/` (see `.maister/docs/INDEX.md`).
