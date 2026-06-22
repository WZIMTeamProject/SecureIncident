# Pre-commit Hooks

The repository uses [pre-commit](https://pre-commit.com/) to auto-fix, lint, and
security-scan changes before they are committed. The configuration is
`.pre-commit-config.yaml` at the repository root.

> This guide describes the canonical config on **`main`**. Some feature branches
> (e.g. `docs_dev`) carry an older config with fewer hooks and a broken ESLint
> hook (see the caveat at the bottom). Treat `main` as the source of truth.

## Install (once per clone)

```bash
# pre-commit itself (if not already installed):
pip install pre-commit       # or: uv tool install pre-commit / brew install pre-commit

# Install the git hook into this repo:
pre-commit install
```

After this, the hooks run automatically on `git commit` against the staged
files. The local toolchain was verified with `pre-commit 4.6.0`.

## Run manually

```bash
# Run all hooks against every file (good before a big PR):
pre-commit run --all-files

# Run all hooks against only staged files:
pre-commit run

# Run a single hook:
pre-commit run ruff --all-files

# Validate the config without running anything:
pre-commit validate-config .pre-commit-config.yaml
```

> Several hooks **modify files** (e.g. `trailing-whitespace`, `end-of-file-fixer`,
> `ruff --fix`, `ruff-format`). When a hook changes a file the commit aborts —
> review the changes, `git add` them, and commit again.

## Configured hooks

| Hook | Scope | What it does |
|------|-------|--------------|
| `trailing-whitespace` | all files | Strips trailing whitespace |
| `end-of-file-fixer` | all files | Ensures a single trailing newline |
| `check-merge-conflict` | all files | Blocks unresolved conflict markers |
| `check-added-large-files` | all files | Blocks accidentally staged large files |
| `ruff` (`--fix`) | `backend/` | Lints + auto-fixes Python (rules `E`, `F`, `I`, `UP`) |
| `ruff-format` | `backend/` | Formats Python (88-char lines, double quotes) |
| `bandit` | `backend/` | Security linter (config in `pyproject.toml`, `-c pyproject.toml`) |
| `pip-audit` | `backend/requirements.txt` | Flags known CVEs in dependencies |
| `vulture` | `backend/` | Flags dead code at ≥80% confidence |
| `eslint` (local) | `Frontend/` | Runs `npx eslint --fix src/` |

Ruff, bandit, and vulture configuration lives in `pyproject.toml` (`[tool.ruff]`,
`[tool.bandit]`, `[tool.vulture]`). The same scanners (`bandit`, `pip-audit`,
`vulture`) also run in CI — see [CI/CD](./ci-cd.md).

> The `pip-audit` hook can fail on dependency advisories even when your change is
> unrelated; that signals a dependency bump is needed, not a problem with your diff.

## Branch caveat — the ESLint hook on older branches

On `main` the local `eslint` hook is correct:

```yaml
entry: bash -c 'cd Frontend && npx eslint --fix src/'
files: ^Frontend/.*\.[jt]sx?$
```

On some unmerged branches (e.g. `docs_dev`) it still reads `cd frontend` /
`files: ^frontend/` (lowercase). Because the real directory is **`Frontend`**, that
pattern never matches staged paths, so the hook silently never runs (and the `cd`
fails on case-sensitive Linux). If you are on such a branch, either rebase on
`main` or run the lint manually:

```bash
cd Frontend && npm run lint
```

See [Testing](./testing.md) for the frontend lint/build commands.
