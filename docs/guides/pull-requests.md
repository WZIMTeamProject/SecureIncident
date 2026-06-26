# Pull Requests

On `main`, opening a PR triggers **build + QA checks** (`ci-checks.yml`,
`backend-qa.yml`, `frontend-qa.yml`): image builds, the `pytest` suite, security
scans, and `npm audit` (see [CI/CD](./ci-cd.md)). The production deploy itself runs
only after merge to `main`. So CI gives feedback on the PR, but it's faster — and
courteous to reviewers — to verify locally first. Keep PRs small and give the
reviewer the context they need.

> **Branch note:** older branches (e.g. `docs_dev`) only run CI on push to `main`,
> so PRs there get no automated checks. On those branches local verification is the
> only gate. Treat `main`'s workflow set as canonical.

## Branching

Never commit directly to `main`. Branch with a type prefix and a short
kebab-case description:

```bash
git checkout -b feature/incident-comments
git checkout -b fix/login-timeout
git checkout -b chore/bump-fastapi
```

| Prefix | Use for |
|--------|---------|
| `feature/<name>` | New functionality |
| `fix/<name>` | Bug fixes |
| `chore/<name>` | Tooling, deps, docs, non-feature maintenance |

## Commits

- Imperative, present-tense subject: `Add incident status filter`, not
  `Added` / `Adds`.
- One concern per commit; don't mix a refactor with a feature.
- Keep secrets out of commits and diffs.

## Before you open the PR

Run the same checks CI will run (and the ones it won't), so nothing breaks after
merge:

```bash
# 1. Hooks / formatting / lint
pre-commit run --all-files

# 2. Backend tests (DB container must be up)
docker compose -f docker-compose.local.yml up -d db
cd backend && uv run pytest

# 3. Frontend checks
cd Frontend && npm run lint && npm run build

# 4. If you touched a Dockerfile / requirements.txt / package.json,
#    confirm the image still builds:
docker compose -f docker-compose.local.yml build backend   # or frontend
```

> On `main` the pre-commit ESLint hook runs on `Frontend/` files; on older
> branches it is a no-op (see [Pre-commit](./pre-commit.md)) — either way, running
> `npm run lint` yourself is the reliable check, since no CI job runs the linter.

## PR checklist

- [ ] Branch named `feature/` · `fix/` · `chore/`
- [ ] `pre-commit run --all-files` is clean
- [ ] `uv run pytest` passes (backend changes)
- [ ] `npm run lint` and `npm run build` pass (frontend changes)
- [ ] Affected Docker image builds (Dockerfile/deps changes)
- [ ] New env vars added to `.env.example`
- [ ] DB schema changes ship an Alembic migration with a working `downgrade()`
- [ ] PR description explains the change and how it was tested

## Review

The reviewer checks correctness, security, auth/permissions, and test coverage.
The author provides context up front: what changed, why, and how it was verified.
Prefer small, focused PRs over large mixed ones.
