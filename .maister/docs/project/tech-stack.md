# Technology Stack

## Overview
This document describes the technology choices and rationale for SecureIncident.

## Languages

### TypeScript (~6.0.2)
- **Usage**: 100% of frontend codebase
- **Rationale**: Type safety and IDE support reduce errors across a 3-person frontend team
- **Configuration**: Bundler mode (`moduleResolution=bundler`, `target=ES2023`, `verbatimModuleSyntax`), TSX for React components.
  - **Important**: `strict` / `noImplicitAny` are **NOT** enabled in `tsconfig.app.json`, and `noUnusedLocals` / `noUnusedParameters` are explicitly `false` for app code. Only `tsconfig.node.json` (build tooling) enables them. `noFallthroughCasesInSwitch` is on.
  - The tsconfig files are the authoritative source for compiler behavior — do not assume strict mode.

### Python (3.14+)
- **Usage**: 100% of backend codebase
- **Rationale**: FastAPI ecosystem maturity, rapid REST API development, strong typing via Pydantic
- **Key Features Used**: Type hints throughout, async/await, Pydantic v2 integration

## Frameworks

### Frontend
- **React 19** (`^19.2.4`) — Hooks-based functional components, modern concurrent features
- **React Router 7** (`^7.14.0`) — Client-side routing with `createBrowserRouter`
- **Vite 8** (`^8.0.4`) — Fast HMR in development, optimized production builds
- **Tailwind CSS 4** (`^4.2.2`) — Utility-first CSS with CSS custom variables for light/dark theming

### Backend
- **FastAPI 0.136+** — Async REST API framework; automatic OpenAPI docs, Pydantic integration
- **Uvicorn 0.49+** — ASGI server running the FastAPI application
- **Pydantic 2.13+** — Request/response validation and serialization
- **pydantic-settings 2.14+** — Settings management via environment variables
- **SQLAlchemy 2.0.50+** — ORM with declarative models and relationship management
- **Alembic 1.18+** — Database schema migration management
- **greenlet 3.5+** — Required for SQLAlchemy async support

### Testing
- **pytest 9.0+** — Backend unit and integration testing
- **pytest-asyncio 1.4+** — Async test support for FastAPI endpoint tests
- **httpx 0.28+** — HTTP client used for API integration testing

## Database

### PostgreSQL (only)
- **Type**: Relational
- **Driver**: `asyncpg 0.31+` — async PostgreSQL driver for SQLAlchemy
- **Rationale**: PostgreSQL is the sole supported database; MySQL support was dropped to reduce complexity
- **Migrations**: Managed via Alembic

## Authentication
- **PyJWT 2.13+** — JWT token generation and validation (stateless auth); `python-jose` was removed due to known CVEs
- **passlib[bcrypt] 1.7+** + **bcrypt 5.0+** — Secure password hashing

## API Specification
- **OpenAPI 3.0.3** — Schema-first API design documented in `docs/api/openapi-core.json` (MVP) and `docs/api/openapi-extended.json`

## Build Tools & Package Management

### Frontend
- **npm** — Package manager (lock file committed for reproducible installs)
- **Vite** — Development server and production bundler

### Backend
- **uv** + `pyproject.toml` — Primary Python dependency management (`uv sync` to install)
- **pip** — Alternative: `pip install -e .` from `pyproject.toml` also works for contributors not using uv
- **python-dotenv 1.2+** — Environment variable loading from `.env`
- **python-multipart 0.0.32+** — Multipart form data parsing (required for FastAPI form endpoints)

## Infrastructure

### Containerization
- **Docker + Docker Compose — implemented.** Multi-stage backend image (`python:3.14-slim`, runs as non-root `appuser`) and multi-stage frontend image (`node:26` builder + `nginx:1.27-alpine` runtime).
- Two compose files: `docker-compose.local.yml` (builds locally, includes Postgres 16 + a Mailpit email sink for development) and `docker-compose.yml` (production — pulls prebuilt GHCR images).
- A `Makefile` provides convenience targets (`make up/down/db/logs/ps`).

### CI/CD
- **GitHub Actions — implemented.** Working CI/CD pipelines (`backend.yml`, `frontend.yml`) run security scanning, tests, and image builds, and deploy to EC2. See `standards/infrastructure/ci-cd.md`.

### Hosting
- **AWS** — Target deployment platform (EC2 + RDS), managed by 3-person DevOps team

## Development Tools

### Linting & Formatting
- **ESLint 9.39.4** (frontend) — Flat config format; plugins: `typescript-eslint`, `react-hooks`, `react-refresh`

### Type Checking
- **TypeScript** (bundler mode; `strict` not enabled — see Languages › TypeScript) — Frontend static analysis
- **Pydantic v2** + Python type hints — Backend runtime and static validation

## Key Dependencies

| Package | Version | Purpose |
|---------|--------|---------|
| react | 19.2.4 | UI framework |
| react-router-dom | 7.14.0 | Client-side routing |
| tailwindcss | 4.2.2  | Utility CSS |
| fastapi | 0.136.3 | Backend REST framework |
| sqlalchemy | >=2.0.50 | ORM |
| alembic | 1.18.4 | DB migrations |
| pydantic | 2.13.4 | Validation |
| pydantic-settings | 2.14.1 | Settings/env management |
| asyncpg | 0.31.0 | PostgreSQL async driver |
| pyjwt | 2.13.0 | JWT (python-jose removed — CVE) |
| passlib | 1.7.4  | Password hashing |
| bcrypt | 5.0.0  | Bcrypt backend for passlib |
| pytest | 9.0.3  | Testing |

## Version Management
- Frontend: Semantic versioning in `package.json` with committed npm lock file
- Backend: Minimum-version constraints in `pyproject.toml`, managed with `uv`

## Pinned Runtimes
- **Backend**: Python **3.14+** (`.python-version` = 3.14, ruff `target-version = py314`, `requires-python = ">=3.14"`).
- **Database**: PostgreSQL **16**.
- **Frontend Node.js**: ⚠️ **inconsistent across config** — `Frontend/mise.toml` = 24, `Frontend/Dockerfile` = `node:26`, `README` = 20+. These should be reconciled to a single pinned version.

---
*Last Updated*: 2026-06-09
*Auto-detected*: React, TypeScript, Vite, Tailwind, FastAPI, SQLAlchemy, Alembic, Pydantic, all npm/pip dependencies
*User-provided*: AWS hosting target, June 18, 2026 deadline; python-jose removed due to CVE
