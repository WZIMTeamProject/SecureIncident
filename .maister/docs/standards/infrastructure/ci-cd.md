# CI/CD Pipeline

## Trigger Rules

Both pipelines trigger only on pushes to the `main` branch. Feature branches do not trigger any automated build or deploy. Merging to `main` is the deployment gate.

- Backend CI: `push` to `main`, paths `backend/**`
- Frontend CI: `push` to `main`, paths `Frontend/**`

Changes to other paths (docs, root configs) do not trigger any pipeline.

## Backend Pipeline

1. **Spin up PostgreSQL 16** service container with health checks
2. **Run `pytest`** against a real PostgreSQL database (connection via `postgresql+asyncpg`)
   - Tests must pass before any build step — failure halts the pipeline
   - No coverage threshold — pass/fail only
3. **Build Docker image** tagged `:latest` and `:<github.sha>`
4. **Push to GHCR** (`ghcr.io/wzimteamproject/secureincident-backend`)
5. **Deploy to EC2** via SSH
6. **Health check**: `docker exec secureincident-backend-1 curl -f http://localhost:8000/health`
   - Deploy is considered failed if the health endpoint does not return 2xx

## Frontend Pipeline

1. **`npm ci`** (reproducible install from `package-lock.json`)
2. **Build Docker image** with `VITE_API_BASE_URL` injected as `--build-arg` from repository variables
   - Never hardcode the API URL — always use `import.meta.env.VITE_API_BASE_URL`
3. **Push to GHCR** (`ghcr.io/wzimteamproject/secureincident-frontend`)
4. **Deploy to EC2** via SSH

## Docker Image Tagging

Every build produces two tags:
- `:latest` — always points to the most recent successful build
- `:<github.sha>` — immutable tag tied to the exact commit

## Runtime Versions

| Component   | CI version | Notes                                                   |
|-------------|------------|---------------------------------------------------------|
| Python      | 3.14       | Matches `requires-python = ">=3.14"` in pyproject.toml  |
| Node.js     | 26         | Frontend CI                                             |
| PostgreSQL  | 16         | CI service container                                    |

## Health Endpoint Contract

`GET /health` must:
- Exist on the backend at port 8000
- Require no authentication
- Return HTTP 2xx
- Respond within the Docker healthcheck timeout

This endpoint is checked by both Docker Compose healthchecks and the CI post-deploy verification.
