# Tooling

## Pre-Commit Hooks

The project uses the `pre-commit` framework. All hooks run automatically on `git commit`. Install hooks with `pre-commit install` after cloning.

| Hook | Scope | What it does |
|------|-------|-------------|
| `trailing-whitespace` | All files | Removes trailing whitespace |
| `end-of-file-fixer` | All files | Ensures files end with exactly one newline |
| `check-merge-conflict` | All files | Blocks files containing merge conflict markers |
| `check-added-large-files` | All files | Blocks unusually large binary files |
| `ruff --fix` | `backend/` Python | Linting (E, F, I, UP rules) with auto-fix |
| `ruff-format` | `backend/` Python | Formatting (double quotes, 88-char lines) |
| `vulture` | `backend/` | Dead code at ≥80% confidence |
| `eslint --fix` | `Frontend/src/` TS/TSX | ESLint with auto-fix |

Auto-fixable violations are corrected in-place; unfixable violations block the commit and must be resolved manually.

## Python Linting & Formatting (Ruff)

Ruff is the single tool for Python linting and formatting in the `backend/` directory.

- **Rules enabled**: `E` (pycodestyle), `F` (pyflakes), `I` (isort), `UP` (pyupgrade)
- **Line length**: 88 characters (ruff default)
- **Quotes**: double quotes enforced by `ruff-format`
- **E501** (line too long) is excluded from linting — the formatter handles length

Per-file ignores (configured in `pyproject.toml`):
- `backend/main.py`, `backend/alembic/env.py`: E402 ignored (top-level side-effect imports allowed)
- `backend/db/models/*.py`: F821 ignored (ORM forward references)

## Dead Code Detection (Vulture)

Vulture scans `backend/` for unused code with `--min-confidence 80`. Remove any unused functions, variables, or imports that vulture flags at ≥80% confidence. Runs as a pre-commit hook and is also configured in `pyproject.toml`.

## Frontend Linting (ESLint)

ESLint runs on all `Frontend/src/` TypeScript/JSX files using:
- `js.configs.recommended`
- `tseslint.configs.recommended`
- `reactHooks.configs.flat.recommended` (enforces rules-of-hooks and exhaustive-deps)
- `reactRefresh.configs.vite` (only export React Refresh-compatible components)

`dist/` is excluded from linting.

## CI Dependencies

- Use `npm ci` (not `npm install`) in CI pipelines — ensures reproducible installs from `package-lock.json`
- Use `docker compose --build` after pulling commits that include new migration files, changed `requirements.txt`, or modified Dockerfiles — without it Docker uses the cached image

## Running Migrations

Run `alembic upgrade head` before starting the backend server. Required on first setup and after pulling any commit that includes a new migration file.

```bash
alembic upgrade head
```
