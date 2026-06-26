# Running the Application

SecureIncident is a two-service application (FastAPI backend + React frontend)
backed by PostgreSQL, with [Mailpit](https://github.com/axllent/mailpit) as a
local email sink. There are three ways to run it locally — pick based on what
you are doing.

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Docker + Docker Compose | latest (v2) | Required for every method (at least the database) |
| Node.js | 20+ (CI and Docker use 26) | Frontend dev server / build |
| npm | bundled with Node.js | |
| Python | 3.14+ | Backend (manual method only) |
| uv | latest | Recommended Python runner — `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

> **Compose v1 vs v2:** the canonical command is `docker compose` (the v2
> plugin, with a space). The `Makefile` still calls the older `docker-compose`
> (hyphenated, v1). On a machine that only has Compose v2 the `make` targets will
> fail — use the `docker compose …` form shown under each target instead.

---

## Method 1 — Docker Compose (full stack)

Runs everything (PostgreSQL, backend, frontend, Mailpit) in containers. The
frontend is served by nginx at **http://localhost** and proxies all `/api/`
requests to the backend. Best for a realistic end-to-end check before pushing.

```bash
# First run, or after a migration / Dockerfile / dependency change:
make up
# equivalent:
docker compose -f docker-compose.local.yml up --build

# Subsequent runs with no code/dependency changes:
docker compose -f docker-compose.local.yml up
```

> **When to use `--build`:** always after pulling a commit that adds a migration
> file, changes `requirements.txt`/`package.json`, or modifies a `Dockerfile`.
> Without it Docker reuses the cached image and your new code is not included.

```bash
# Stop and remove containers (data preserved in the postgres_data volume):
make down
# equivalent: docker compose -f docker-compose.local.yml down

# Stop and wipe all data:
docker compose -f docker-compose.local.yml down -v

# Follow live logs:
make logs
# equivalent: docker compose -f docker-compose.local.yml logs -f

# Container status:
make ps
# equivalent: docker compose -f docker-compose.local.yml ps
```

| Service | URL |
|---------|-----|
| App (frontend via nginx) | http://localhost |
| API (proxied) | http://localhost/api |
| Mailpit web UI | http://localhost:8025 |

---

## Method 2 — Manual (fast iteration)

Run only the database (and Mailpit) in containers; run the backend and frontend
from source for hot reload. Best for day-to-day development.

**Step 1 — Start infrastructure containers**

```bash
# Database only:
make db
# equivalent: docker compose -f docker-compose.local.yml up -d db

# Database + Mailpit:
docker compose -f docker-compose.local.yml up -d db mailpit
```

**Step 2 — Backend** (from `backend/`)

```bash
cd backend
alembic upgrade head        # apply any pending migrations first
uvicorn main:app --reload   # dev server with hot reload
```

| Endpoint | URL |
|----------|-----|
| API base | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

**Step 3 — Frontend** (from `Frontend/`)

```bash
cd Frontend
npm install     # first run only
npm run dev
```

App available at **http://localhost:5173**. In this mode the dev server talks
directly to the backend on port 8000 via `VITE_API_URL` — no nginx proxy is
involved.

---

## Method 3 — Building individual services

Verify a single service builds without starting the whole stack — useful before
pushing a PR that touches a `Dockerfile`, `requirements.txt`, or `package.json`.

```bash
# Build one image:
docker compose -f docker-compose.local.yml build backend
docker compose -f docker-compose.local.yml build frontend

# Run a subset of services:
docker compose -f docker-compose.local.yml up db backend      # backend only
docker compose -f docker-compose.local.yml up db frontend      # frontend only
```

---

## Environment variables

### Backend — `SecureIncident/.env` (repository root)

Copy `.env.example` and adjust. Generate a real key with
`python -c "import secrets; print(secrets.token_hex(32))"`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL asyncpg connection string |
| `SECRET_KEY` | Yes | — | JWT signing key (32-byte hex recommended) |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | Access token lifetime |
| `REMEMBER_ME_EXPIRE_MINUTES` | No | `10080` | "Remember me" token lifetime |
| `PASSWORD_RESET_EXPIRE_MINUTES` | No | `30` | Reset token lifetime |
| `ALLOWED_ORIGINS` | No | `["http://localhost:5173"]` | CORS origins (JSON list) |
| `SMTP_HOST` | No | `mailpit` | SMTP host (`localhost` when running the backend outside Docker) |
| `SMTP_PORT` | No | `1025` | SMTP port |
| `SMTP_USER` | No | *(empty)* | SMTP username (empty for Mailpit) |
| `SMTP_PASSWORD` | No | *(empty)* | SMTP password (empty for Mailpit) |
| `SMTP_FROM` | No | `noreply@localhost` | From address |
| `SMTP_TLS` | No | `False` | `True` for production SMTP |
| `FRONTEND_URL` | No | `http://localhost:5173` | Base URL used in password-reset links |

> **Production SMTP var name:** the backend reads `SMTP_USER`. On `main`, the
> production `docker-compose.yml` maps it explicitly (`SMTP_USER: ${SMTP_USERNAME}`),
> so the **host** environment variable is `SMTP_USERNAME` while the container value
> is `SMTP_USER`. (On older branches like `docs_dev` this mapping is missing and the
> names look mismatched.)

### Frontend — `Frontend/.env.local`

```env
# URL of the running backend API (manual/dev mode)
VITE_API_URL=http://localhost:8000
```

In Docker builds the API base is injected at build time via the
`VITE_API_BASE_URL` build argument instead (see [CI/CD](./ci-cd.md)).

---

## Password reset & email (local)

Mailpit captures all outbound email without delivering it.

```bash
# Request a reset (token is emailed):
curl -s -X POST http://localhost:8000/api/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email_or_username": "your_username_or_email"}'
```

Open **http://localhost:8025**, copy the `token` from the reset link, then:

```bash
curl -s -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"reset_token": "<token>", "new_password": "NewPass1!"}'
```

The endpoint always returns `204` regardless of email delivery (delivery runs in
a background task). Tokens expire after 30 minutes; requesting a new reset
invalidates any pending token.
