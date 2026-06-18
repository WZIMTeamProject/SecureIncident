# SecureIncident

Web-based incident reporting platform — React 19 frontend + FastAPI backend + PostgreSQL.

## Structure

```
SecureIncident/
├── Frontend/                 # React 19 + Vite + Tailwind CSS
├── backend/                  # FastAPI + SQLAlchemy + Alembic
├── docs/api/                 # OpenAPI specification
├── docker-compose.yml        # production
├── docker-compose.local.yml  # local development
└── .env                      # environment variables (gitignored)
```

---

## Running the Application

### Method 1 — Docker Compose (recommended before committing)

Runs the full stack (PostgreSQL, backend, frontend, Mailpit) in containers.
The frontend is served at **http://localhost** and proxies all `/api/` requests to the backend.

```bash
# First run, or after a migration or Dockerfile change:
make up
# equivalent:
docker compose -f docker-compose.local.yml up --build

# Subsequent runs with no code/dependency changes:
docker compose -f docker-compose.local.yml up
```

> **When to use `--build`:** always after pulling a commit that adds a migration file,
> changes `requirements.txt`, or modifies a `Dockerfile`. Without it Docker uses the
> cached image and your new code won't be included.

```bash
# Stop and remove containers (data is preserved in the postgres_data volume)
make down
# equivalent:
docker compose -f docker-compose.local.yml down

# Stop and wipe all data
docker compose -f docker-compose.local.yml down -v
```

Follow live logs while the stack is running:

```bash
make logs
# equivalent:
docker compose -f docker-compose.local.yml logs -f
```

---

### Method 2 — Manual (quick iteration)

Start only the database and Mailpit containers (their ports are exposed for direct local access),
then run the backend and frontend from source for fast reloads.

**Step 1 — Start infrastructure containers:**

```bash
# Database only:
make db
# equivalent:
docker compose -f docker-compose.local.yml up -d db

# Database + Mailpit:
docker compose -f docker-compose.local.yml up -d db mailpit
```

**Step 2 — Start the backend** (from the `backend/` directory):

```bash
# Apply any pending migrations first:
cd backend
alembic upgrade head

# Start the dev server with hot reload:
uvicorn main:app --reload
```

API available at **http://localhost:8000** · Swagger UI at **http://localhost:8000/docs**

**Step 3 — Start the frontend** (from the `Frontend/` directory):

```bash
cd Frontend
npm install          # first run only
npm run dev
```

App available at **http://localhost:5173**

> When running manually the frontend dev server (`npm run dev`) talks directly to the
> backend on port 8000 via `VITE_API_URL` — no nginx proxy is involved.
> See [Frontend — Environment Variables](#step-2--configure-environment-variables-1) for the required `.env.local`.

---

### Method 3 — Building individual services

Use these commands to verify a service builds correctly without starting the full stack —
useful before pushing a PR, after changing a `Dockerfile`, or after adding/removing dependencies.

**Build only one service:**

```bash
docker compose -f docker-compose.local.yml build backend
docker compose -f docker-compose.local.yml build frontend
```

**Run a subset of services** (e.g. to test the backend without the frontend):

```bash
# Database + backend only:
docker compose -f docker-compose.local.yml up db backend

# Database + frontend only (frontend needs a running backend to be useful):
docker compose -f docker-compose.local.yml up db frontend
```

**Check container status:**

```bash
make ps
# equivalent:
docker compose -f docker-compose.local.yml ps
```

> Run individual service builds after every change to `Dockerfile`, `requirements.txt`,
> `package.json`, or `package-lock.json` — and always before opening a PR that touches
> those files.

---

# Backend — SecureIncident API

FastAPI + SQLAlchemy + Alembic + PostgreSQL.

---

## Prerequisites

| Tool                    | Version                                                      |
|-------------------------|--------------------------------------------------------------|
| Python                  | 3.14+                                                        |
| uv                      | latest (`curl -LsSf https://astral.sh/uv/install.sh \| sh`) |
| pip                     | bundled with Python (alternative to uv)                      |
| Docker + Docker Compose | latest (for database + email sink)                           |

---

## First-Time Setup

### Step 1 — Start Docker services

From the **repository root** (`SecureIncident/`), start PostgreSQL and the local email sink:

```bash
docker compose up -d
```

This starts two containers:

| Container               | Purpose                    | Port(s)          |
|-------------------------|----------------------------|------------------|
| `secure_incident_db`    | PostgreSQL 16 database     | 5432             |
| `secure_incident_mailpit` | Mailpit — local email sink | 1025 (SMTP), 8025 (web UI) |

To verify both are running:

```bash
docker compose ps
```

---

### Step 2 — Configure Environment Variables

Create `.env` in the **repository root** (`SecureIncident/.env`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/secure_incident

# JWT — generate a key with:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["http://localhost:5173"]

# Email (local dev — Mailpit)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@localhost
SMTP_TLS=False
FRONTEND_URL=http://localhost:5173
```

> **Production:** replace the `SMTP_*` values with your real SMTP provider credentials (SendGrid, SES, Mailgun, etc.) and set `SMTP_TLS=True`.

---

### Step 3 — Install Dependencies

From the **repository root** (where `pyproject.toml` lives):

```bash
# with uv (recommended)
uv sync

# or with pip
pip install -r backend/requirements.txt
```

---

### Step 4 — Run Migrations

From the `backend/` directory:

```bash
alembic upgrade head
```

Run this once on first setup and again after pulling changes that include new migrations.

---

## Running the API

From the `backend/` directory:

```bash
uvicorn main:app --reload
```

| Endpoint         | URL                        |
|------------------|----------------------------|
| API base         | http://localhost:8000      |
| Interactive docs | http://localhost:8000/docs |

---

## Running Tests

Tests require the database container to be running (`docker compose up -d`). The test suite uses the same `secure_incident` database as development — each test runs inside a transaction that is rolled back afterwards, so no data persists between tests.

From the `backend/` directory:

```bash
# with uv (recommended)
uv run pytest

# without uv — activate the virtualenv first, then use pytest directly
source ../.venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate       # Windows
pytest
```

Run a specific file:

```bash
uv run pytest tests/test_profiles.py -v
pytest tests/test_profiles.py -v          # without uv (venv active)
```

> **Without uv:** `uv run` is a shorthand for "run inside the managed virtualenv". The virtualenv lives at `.venv/` in the repository root. Activating it manually gives `pytest` the same environment — the `uv` binary itself is not required at test runtime.

---

## Email Service & Password Reset

The password reset flow sends a reset link by email using an async background task (non-blocking — the endpoint always returns 204 regardless of email delivery).

### How it works

1. `POST /api/auth/request-password-reset` with `{"email_or_username": "..."}` — generates a token and emails the reset link
2. User clicks the link: `http://localhost:5173/reset-password?token=<token>`
3. `POST /api/auth/reset-password` with `{"reset_token": "...", "new_password": "..."}` — validates and applies the new password

Tokens expire after 30 minutes. Requesting a new reset invalidates any pending token.

### Testing locally with Mailpit

Mailpit is a local SMTP sink — it captures all outbound email without delivering anything.

**Start Mailpit** (included in `docker compose up -d`).

**Send a test reset:**

```bash
curl -s -X POST http://localhost:8000/api/auth/request-password-reset \
  -H "Content-Type: application/json" \
  -d '{"email_or_username": "your_username_or_email"}'
```

**View captured email:** open [http://localhost:8025](http://localhost:8025) in the browser.

The email contains the reset link with the raw token. Copy the `token` query parameter and use it in the confirm step:

```bash
curl -s -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"reset_token": "<token>", "new_password": "NewPass1!"}'
```

You can also test both steps via Swagger at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Daily Workflow

See [Running the Application](#running-the-application) at the top of this README for all startup options.

Quick reference for manual backend dev:

```bash
# 1. Start the database
docker compose -f docker-compose.local.yml up -d db

# 2. Apply pending migrations (from backend/)
alembic upgrade head

# 3. Start the API server (from backend/)
uvicorn main:app --reload

# Stop: Ctrl+C, then:
docker compose -f docker-compose.local.yml down
```

---

## Environment Variables Reference

| Variable                        | Required | Default                       | Description                                        |
|---------------------------------|----------|-------------------------------|----------------------------------------------------|
| `DATABASE_URL`                  | Yes      | —                             | PostgreSQL asyncpg connection string               |
| `SECRET_KEY`                    | Yes      | —                             | JWT signing key (32-byte hex recommended)          |
| `ALGORITHM`                     | No       | `HS256`                       | JWT algorithm                                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | No       | `30`                          | Access token lifetime in minutes                   |
| `PASSWORD_RESET_EXPIRE_MINUTES` | No       | `30`                          | Password reset token lifetime in minutes           |
| `ALLOWED_ORIGINS`               | No       | `["http://localhost:5173"]`   | CORS allowed origins (JSON list)                   |
| `SMTP_HOST`                     | No       | `mailpit`                     | SMTP server hostname (`localhost` when running locally outside Docker) |
| `SMTP_PORT`                     | No       | `1025`                        | SMTP server port                                   |
| `SMTP_USER`                     | No       | *(empty)*                     | SMTP username (leave empty for Mailpit)            |
| `SMTP_PASSWORD`                 | No       | *(empty)*                     | SMTP password (leave empty for Mailpit)            |
| `SMTP_FROM`                     | No       | `noreply@localhost`           | From address on outbound emails                    |
| `SMTP_TLS`                      | No       | `False`                       | Enable TLS (`True` for production SMTP)            |
| `FRONTEND_URL`                  | No       | `http://localhost:5173`       | Base URL used in the password reset email link     |

# Frontend — SecureIncident

React 19 + TypeScript + Vite + Tailwind CSS 4.

---

## Prerequisites

| Tool    | Version              |
|---------|----------------------|
| Node.js | 20+                  |
| npm     | bundled with Node.js |

---

## First-Time Setup

### Step 1 — Install Dependencies

From the `Frontend/` directory:

```bash
npm install
```

### Step 2 — Configure Environment Variables

Create `Frontend/.env.local`:

```env
# URL of the running backend API
VITE_API_URL=http://localhost:8000
```

> The backend must be running before you start the frontend. See [`Backend-SecureIncident-API`](#backend--secureincident-api) for setup instructions.

---

## Running the App

```bash
npm run dev
```

App available at: http://localhost:5173

Hot module replacement is enabled — changes to source files reload instantly in the browser.

---

## Other Commands

```bash
# Type-check and build for production
npm run build

# Preview the production build locally
npm run preview

# Run the linter
npm run lint
```

---

## Project Structure

```
Frontend/
├── public/          # Static assets served as-is
└── src/             # Application source
```
