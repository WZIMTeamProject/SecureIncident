# Technology Stack

## Overview
This document describes the technology choices and rationale for SecureIncident.

## Languages

### TypeScript (~6.0.2)
- **Usage**: 100% of frontend codebase
- **Rationale**: Type safety and IDE support reduce errors across a 3-person frontend team
- **Key Features Used**: Strict mode, ES2023 target, TSX for React components, `noUnusedLocals`, `noUnusedParameters`

### Python (3.x)
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
- **FastAPI 0.104.1** — Async REST API framework; automatic OpenAPI docs, Pydantic integration
- **Uvicorn 0.24.0** — ASGI server running the FastAPI application
- **Pydantic 2.5.0** — Request/response validation and serialization
- **SQLAlchemy 2.0.23** — ORM with declarative models and relationship management
- **Alembic 1.12.1** — Database schema migration management

### Testing
- **pytest 7.4.3** — Backend unit and integration testing
- **pytest-asyncio 0.21.1** — Async test support for FastAPI endpoint tests
- **httpx 0.25.2** — HTTP client used for API integration testing

## Database

### PostgreSQL (primary) / MySQL (alternative)
- **Type**: Relational
- **ORM**: SQLAlchemy 2.0 (`psycopg2-binary` for PostgreSQL, `PyMySQL 1.1.0` for MySQL)
- **Rationale**: Dual-database support allows development flexibility; PostgreSQL is the target for production (AWS RDS)
- **Migrations**: Managed via Alembic

## Authentication
- **python-jose 3.3.0** + **PyJWT 2.12.1** — JWT token generation and validation (stateless auth)
- **passlib[bcrypt] 1.7.4** — Secure password hashing

## API Specification
- **OpenAPI 3.0.3** — Schema-first API design documented in `docs/api/openapi-core.json` (MVP) and `docs/api/openapi-extended.json`

## Build Tools & Package Management

### Frontend
- **npm** — Package manager (lock file committed for reproducible installs)
- **Vite** — Development server and production bundler

### Backend
- **pip** + `requirements.txt` — Python dependency management with pinned versions
- **python-dotenv 1.0.0** — Environment variable loading from `.env`

## Infrastructure

### Containerization
- Docker + Docker Compose — Planned (not yet configured); needed for AWS deployment

### CI/CD
- GitHub Actions — Planned for automated test → build → deploy pipeline

### Hosting
- **AWS** — Target deployment platform (ECS/Fargate + RDS or EC2 + RDS), managed by 3-person DevOps team

## Development Tools

### Linting & Formatting
- **ESLint 9.39.4** (frontend) — Flat config format; plugins: `typescript-eslint`, `react-hooks`, `react-refresh`

### Type Checking
- **TypeScript** strict mode — Frontend static analysis
- **Pydantic v2** + Python type hints — Backend runtime and static validation

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^19.2.4 | UI framework |
| react-router-dom | ^7.14.0 | Client-side routing |
| tailwindcss | ^4.2.2 | Utility CSS |
| fastapi | 0.104.1 | Backend REST framework |
| sqlalchemy | 2.0.23 | ORM |
| alembic | 1.12.1 | DB migrations |
| pydantic | 2.5.0 | Validation |
| python-jose | 3.3.0 | JWT |
| passlib | 1.7.4 | Password hashing |
| pytest | 7.4.3 | Testing |

## Version Management
- Frontend: Semantic versioning in `package.json` with committed npm lock file
- Backend: Pinned exact versions in `requirements.txt`

---
*Last Updated*: 2026-05-04
*Auto-detected*: React, TypeScript, Vite, Tailwind, FastAPI, SQLAlchemy, Alembic, Pydantic, all npm/pip dependencies
*User-provided*: AWS hosting target, 5-6 week delivery timeline
