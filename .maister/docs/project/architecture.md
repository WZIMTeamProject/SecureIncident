# System Architecture

## Overview
SecureIncident is a monorepo containing a React SPA frontend, a FastAPI REST backend, and a relational database layer. The system follows a client-server architecture with a clearly defined API contract (OpenAPI 3.0.3) separating the frontend from the backend.

## Architecture Pattern
**Pattern**: Monorepo — Client-Server (SPA + Layered REST API)

The frontend is a single-page application communicating with the backend exclusively via REST API calls. The backend implements a layered architecture (routes → schemas/dependencies → ORM models) backed by a relational database. Contracts are defined first via OpenAPI specification, then implemented.

## System Structure

### Frontend (React SPA)
- **Location**: `Frontend/`
- **Purpose**: User interface for incident reporting, project management, and dashboards
- **Key Files**:
  - `Frontend/src/main.tsx` — Application entry point, React Router setup
  - `Frontend/src/App.tsx` — Root component
  - `Frontend/src/index.css` — Global styles (Tailwind CSS + CSS custom variables)
  - `Frontend/vite.config.ts` — Build and dev-server configuration
  - `Frontend/package.json` — Dependencies and npm scripts

### Backend API (FastAPI)
- **Location**: `backend/` (branch: `backend_api`)
- **Purpose**: REST API server exposing all system functionality
- **Key Files**:
  - `backend/main.py` — FastAPI app entry point, router registration under `/api` prefix
  - `backend/api/routes/` — Endpoint handlers: `auth`, `organization`, `projects`, `incidents`, `roles`, `categories`
  - `backend/api/schemas/` — Pydantic request/response models per domain
  - `backend/api/dependencies/` — Dependency injection: `auth.py` (JWT), `db.py` (session), `permissions.py` (RBAC)

### Database Layer (SQLAlchemy)
- **Location**: `backend/db/` (branch: `database_models`)
- **Purpose**: ORM models, entity relationships, and database session management
- **Key Files**:
  - `backend/db/models/` — Entities: `User`, `Organization`, `Project`, `Incident`, `Role`, `Category`, `Comment`, `IncidentLog`, `UserProject`
  - `backend/db/base.py` — SQLAlchemy declarative base

### API Specification
- **Location**: `docs/api/`
- **Purpose**: OpenAPI contract defined before implementation (schema-first)
- **Files**:
  - `docs/api/openapi-core.json` — Core MVP endpoints (v0.1.1)
  - `docs/api/openapi-extended.json` — Extended/planned endpoints

## Domain Model

```
Organization
  └── Projects (1:many)
        ├── Roles (project-scoped)
        ├── Categories (project-scoped)
        └── Incidents (1:many)
              ├── Comments (1:many)
              └── IncidentLogs (audit trail)

User
  ├── Organization membership (optional — mutually exclusive with private-only mode)
  └── Projects (many-to-many via UserProject)
```

**Key Constraint**: A user belongs to one organization OR uses private projects only — not both.

## Data Flow

```
Browser (React SPA)
  │  HTTP request
  ▼
FastAPI /api/* endpoint
  │  JWT validation (dependencies/auth.py)
  │  Permission check (dependencies/permissions.py)
  │  SQLAlchemy session (dependencies/db.py)
  ▼
Route handler (api/routes/*.py)
  │  Pydantic schema validation
  ▼
Database (PostgreSQL / MySQL via SQLAlchemy ORM)
  │
  ▼
Pydantic response serialization → JSON
```

## External Integrations
- **Database**: PostgreSQL (production target) or MySQL (development alternative) via SQLAlchemy
- **Authentication**: Stateless JWT tokens — no external identity provider

## Configuration
- **Backend**: `python-dotenv` loads `.env` file (database URL, JWT secret, etc.)
- **Frontend**: Vite environment variables (`VITE_API_URL`, etc. with `VITE_` prefix)
- **Production**: AWS Secrets Manager / SSM Parameter Store (planned by DevOps team)

## Deployment Architecture

Target: AWS cloud deployment within 5-6 weeks, managed by the 3-person DevOps team.

```
[Browser]
    │ HTTPS
    ▼
[AWS CloudFront + S3]          ← React SPA static build
    │
    ▼ API requests
[AWS Application Load Balancer]
    │
    ▼
[AWS ECS/Fargate or EC2]       ← FastAPI + Uvicorn Docker container
    │
    ▼
[AWS RDS (PostgreSQL)]         ← Managed relational database
```

CI/CD flow via GitHub Actions: `push` → run tests → build Docker image → push to ECR → deploy to ECS.

---
*Based on codebase analysis performed 2026-05-04*
