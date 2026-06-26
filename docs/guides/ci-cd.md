# CI/CD

Continuous integration and deployment run on **GitHub Actions**, defined in
`.github/workflows/`. This guide describes the canonical setup on the **`main`**
branch — the integration target where the full pipeline lives.

> **Branch note:** some feature branches (e.g. `docs_dev`) carry an older, smaller
> workflow set. If a workflow described here is missing on your branch, it has not
> been merged from `main` yet. Treat `main` as the source of truth.

There are **five** workflows split into two roles:

| Role | Workflow | Trigger |
|------|----------|---------|
| **Pre-merge checks** | `ci-checks.yml` | push to any non-`main` branch + PR to `main` |
| | `backend-qa.yml` | push touching `backend/**` (any branch) + PR to `main` |
| | `frontend-qa.yml` | push touching `Frontend/**` + PR to `main` |
| **Production deploy** | `backend-ci.yml` | push to `main` touching `backend/**` |
| | `frontend-ci.yml` | push to `main` touching `Frontend/**` |

So: **branches and PRs get build + QA checks; merging to `main` triggers the
production deploy.** Verify locally first (see [Pull requests](./pull-requests.md)),
but CI will also give you feedback on the PR.

---

## Pre-merge checks (branches & PRs)

### `ci-checks.yml` — CI Checks
Triggers on push to any branch except `main`, and on PRs to `main`. Builds both
the frontend and backend Docker images with `push: false` — a fast "does it still
build?" gate.

### `backend-qa.yml` — Backend QA (Tests & Build Checks)
Three sequential jobs:

1. **security-checks** — installs `bandit`, `pip-audit`, `vulture`, runs each over
   the backend, writes results to `docs/bandit.txt`, `docs/pip-audit.txt`,
   `docs/vulture.txt`, and **commits + pushes** them back to the repo
   (`contents: write`). This is why those `docs/*.txt` files are tracked on `main`.
2. **run-tests** — `postgres:16` service container, installs
   `backend/requirements.txt`, runs `pytest` against
   `postgresql+asyncpg://test:test@localhost:5432/test`.
3. **test-docker-build** — backend image `docker build` dry-run (`push: false`).

### `frontend-qa.yml` — Frontend QA (Audit & Build Checks)
- **frontend-qa** — `npm ci` + `npm audit --audit-level=high`.
- **test-frontend-build** — frontend image `docker build` dry-run.

> **Heads-up:** `npm audit --audit-level=high` currently reports high-severity
> advisories, so this step fails until the dependencies are bumped. Run
> `npm audit` locally to see the current set.

---

## Production deploy (`main` only)

### `backend-ci.yml` — Backend Production Deploy
Runs on push to `main` under `backend/**`:

1. **uv** (`astral-sh/setup-uv@v4`, Python 3.14) → `uv sync` → `uv run pytest`
   against a `postgres:16` service. Failing tests stop the deploy.
2. **Export requirements** — `uv export --frozen --no-dev -o backend/requirements.txt`
   so the Docker image installs the exact locked set. (`requirements.txt` is a
   generated artifact — edit `pyproject.toml`/`uv.lock`, not it directly.)
3. **Build & push** `ghcr.io/wzimteamproject/secureincident-backend:latest` and
   `:<github.sha>` to GHCR.
4. **Deploy to EC2** over SSH: fetch secrets, `docker compose pull backend`,
   `docker compose up -d --force-recreate backend`, then a 60-second health-check
   loop on `http://localhost:8000/health`.

### `frontend-ci.yml` — Frontend Production Deploy
Runs on push to `main` under `Frontend/**`:

1. **Build & push** the frontend image with `VITE_API_BASE_URL` injected as a
   build argument (never hardcoded), tagged `:latest` and `:<github.sha>`.
2. **Deploy to EC2**: `docker compose pull frontend`,
   `docker compose up -d --force-recreate frontend`.

The production stack on EC2 is `docker-compose.yml`, which pulls the `:latest`
GHCR images and terminates TLS in the frontend nginx container (Cloudflare origin
certs mounted from the host).

---

## Required GitHub configuration

| Name | Kind | Used for |
|------|------|----------|
| `GITHUB_TOKEN` | secret (built-in) | GHCR auth; QA security-checks commit |
| `SSH_PRIVATE_KEY` | secret | SSH into the EC2 host |
| `EC2_HOST` | variable | EC2 hostname/IP |
| `EC2_USER` | variable | EC2 SSH user |
| `VITE_API_BASE_URL` | variable | Frontend API base injected at build time |

GHCR images are published under `ghcr.io/wzimteamproject/`.

---

## Known inconsistencies (worth a `fix/` PR)

- **Python version drift:** `backend-qa.yml` `run-tests` pins **Python 3.12**,
  while `backend-ci.yml` and `pyproject.toml` target **3.14**. The QA tests run on
  a different interpreter than production.
- **`frontend-qa` audit gate fails** on the current high-severity advisories.
- **QA auto-commit:** `backend-qa.yml` `security-checks` commits scan results on
  every push (any branch), which can create noisy commits and may be rejected on
  protected branches.

---

## The `/health` endpoint

Deploy verification depends on `GET /health` on port 8000 returning `2xx` with no
auth. It also backs the backend container's Docker healthcheck (`docker-compose*.yml`),
which gates the frontend's `depends_on`. Keep it unauthenticated and fast.
