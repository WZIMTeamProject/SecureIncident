# SecureIncident

Web-based incident reporting platform — React 19 frontend + FastAPI backend + PostgreSQL.

## Structure

```
SecureIncident/
├── Frontend/    # React 19 + Vite + Tailwind CSS
├── backend/     # FastAPI + SQLAlchemy + Alembic
└── docs/api/    # OpenAPI specification
```
# Backend — SecureIncident API

FastAPI + SQLAlchemy + Alembic + PostgreSQL.

---

## Prerequisites

| Tool                    | Version                                                     |
|-------------------------|-------------------------------------------------------------|
| Python                  | 3.14+                                                       |
| uv                      | latest (`curl -LsSf https://astral.sh/uv/install.sh \| sh`) |
| pip                     | bundled with Python (alternative to uv)                     |
| Docker + Docker Compose | latest (for the local DB option)                            |

---

## First-Time Setup

### Step 1 — Choose a Database

Pick **one** option below.

---

#### Option A — Docker (recommended for local development)

The `docker-compose.yml` should be in `backend/` directory. Start PostgreSQL 16:

```bash
docker compose up -d
```

**`docker-compose.yml` contents:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    container_name: secure_incident_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: secure_incident
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Connection string for this setup:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/secure_incident
```

---

#### Option B — Neon (serverless PostgreSQL)

1. Create a project at https://neon.tech
2. Go to **Connection Details** → select **asyncpg** as the driver
3. Copy the connection string:
   ```
   postgresql+asyncpg://user:password@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

---

#### Option C — Supabase

1. Create a project at https://supabase.com
2. Go to **Project Settings → Database → Connection string → URI**
3. Change the scheme from `postgresql://` to `postgresql+asyncpg://`:
   ```
   postgresql+asyncpg://postgres:your-password@db.xxxx.supabase.co:5432/postgres
   ```

> If you get SSL errors, append `?ssl=true` to the connection string.

---

### Step 2 — Configure Environment Variables

Create `core/.env` with the following content:

```env
# Database — replace with your connection string from Step 1
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/secure_incident

# JWT signing key — generate one with:
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=change-me-in-production

# Token settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS — list of origins allowed to call the API
ALLOWED_ORIGINS=["http://localhost:5173"]
```

---

### Step 3 — Install Dependencies

From the **repository root** (one level up, where `pyproject.toml` lives):

```bash
# with uv (recommended)
uv sync

# or with pip
pip install -r requirements.txt
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

```bash
uvicorn main:app --reload
```

| Endpoint         | URL                        |
|------------------|----------------------------|
| API base         | http://localhost:8000      |
| Interactive docs | http://localhost:8000/docs |

---

## Daily Workflow

```bash
# Start database (Docker option only)
docker compose up -d

# Start API server
uvicorn main:app --reload
```

## Stopping

```bash
# Stop API: Ctrl+C

# Stop database
docker compose down

# Stop database and wipe all data
docker compose down -v
```

---

## Environment Variables Reference

| Variable                      | Required   | Default                     | Description                               |
|-------------------------------|------------|-----------------------------|-------------------------------------------|
| `DATABASE_URL`                | Yes        | —                           | PostgreSQL asyncpg connection string      |
| `SECRET_KEY`                  | Yes        | —                           | JWT signing key (32-byte hex recommended) |
| `ALGORITHM`                   | No         | `HS256`                     | JWT algorithm                             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No         | `30`                        | Token lifetime in minutes                 |
| `ALLOWED_ORIGINS`             | No         | `["http://localhost:5173"]` | CORS allowed origins (JSON list)          |

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
