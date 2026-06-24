# CI/CD Pipeline

Two GitHub Actions workflows drive CI/CD: `.github/workflows/backend.yml` and `.github/workflows/frontend.yml`.

## Trigger Rules

Both pipelines are **path-filtered** and run on three events: `push`, `pull_request` targeting `main`, and manual `workflow_dispatch`.

- Backend CI (`backend.yml`): paths `backend/**`
- Frontend CI (`frontend.yml`): paths `Frontend/**`

Security scanning, tests, and a dry-run image build run on **pull requests to `main`**. Only the **deploy** job is gated to `main` via `if: github.ref == 'refs/heads/main'` — so deployment happens only after merge, while everything else validates PRs.

## Backend Job Gate Chain

The backend pipeline enforces a strict `needs:` dependency order. A failure in an earlier job blocks all later jobs:

```
security-scan → test → build → deploy
```

All backend CI jobs set up the toolchain with `astral-sh/setup-uv@v4` pinned to `python-version: '3.14'`, followed by `uv sync`.

### 1. security-scan

- **bandit** — SAST over `api`, `core`, `db`, `services`, `main.py`
- **pip-audit** — CVE audit of `requirements.txt` (`--no-deps --disable-pip`)
- **vulture** — dead-code detection (`--min-confidence 80`, excluding tests, ignoring `cls`)

Tool execution errors fail the job; findings are written to the GitHub step summary.

### 2. test

- `uv run pytest` against a **PostgreSQL 16** service container (with `pg_isready` healthcheck)
- `DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/test`
- No DB mocking — tests run against a real database
- Tests must pass before any build step

### 3. build

- Non-pushing **dry-run** Docker build (`push: false`) as a quality gate — validates the image builds without publishing it.

### 4. deploy (main only)

Runs only when `github.ref == 'refs/heads/main'`:

1. Export a frozen, dev-free requirements file:
   ```bash
   uv export --frozen --no-dev -o backend/requirements.txt
   ```
2. Build and push images to GHCR, each tagged both `:latest` and `:${{ github.sha }}`:
   - `ghcr.io/wzimteamproject/secureincident-backend`
   - `ghcr.io/wzimteamproject/secureincident-frontend`
3. Deploy via `appleboy/ssh-action` to EC2:
   ```bash
   docker compose pull
   docker compose up -d --force-recreate
   ```
4. Verify the deployment with a health-check loop:
   ```bash
   timeout 60 bash -c 'until curl -fs http://localhost:8000/health; do sleep 3; done'
   ```

## Frontend Pipeline

- `npm ci` on **Node 26** (reproducible install from `package-lock.json`)
- `npm audit --audit-level=high` — blocking gate
- Dry-run Docker build as a quality gate
- `VITE_API_BASE_URL` injected as a Docker `--build-arg` (never hardcoded — always read via `import.meta.env.VITE_API_BASE_URL`)
- Deploy job gated to `main`, same EC2 SSH deploy pattern as backend

## PR Conflict Check (pull_request only)

A `pr-conflict-check` job runs on pull requests:

- Fetches `origin/main`
- Uses `git merge-tree` to detect merge conflicts against `main`
- Uses `git rev-list --count HEAD..origin/main` to report how far behind `main` the branch is

Results are written to the GitHub step summary.

## Docker Image Tagging

Every deploy build produces two tags:

- `:latest` — always points to the most recent successful build
- `:<github.sha>` — immutable tag tied to the exact commit

## Health Endpoint Contract

`GET /health` must:

- Exist on the backend at port 8000
- Require no authentication
- Return HTTP 2xx
- Respond within the Docker healthcheck timeout

This endpoint is checked by both Docker Compose healthchecks and the CI post-deploy verification loop.
