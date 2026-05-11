# Development Conventions

## Git Workflow

- **Branch naming**: `feature/<short-description>`, `fix/<short-description>`, `chore/<short-description>`
- **Commit messages**: imperative present tense — "Add incident assignment endpoint", not "Added" or "Adding"
- **One concern per commit** — don't mix feature work with formatting cleanup
- **PR description**: what changed and why; reference the task/ticket number
- **Never commit to `main` directly** — all changes go through pull requests with at least one reviewer

## Environment Variables

- Never commit secrets, API keys, database credentials, or JWT secrets
- Maintain a `.env.example` with all required keys (no values) committed to the repo
- Each developer creates their own `.env` from `.env.example`
- Prefix frontend env vars with `VITE_` (Vite requirement)
- Backend reads env vars via `python-dotenv`; fail fast on startup if required vars are missing

## Dependencies

- Add a dependency only when it solves a real, current problem
- Pin exact versions in `requirements.txt`; use `^` ranges in `package.json` but commit the lock file
- Document why a non-obvious dependency was added (in tech-stack.md or PR description)
- Remove unused dependencies promptly

## Code Review

- Author provides context in the PR description (what, why, how to test)
- Reviewer checks: correctness, security (especially auth/permissions), test coverage, standards compliance
- Resolve all open comments before merging
- Keep PRs small and focused — easier to review, faster to merge

## Secrets & Security

- Use `.gitignore` to block `.env`, `*.key`, `*.pem`, and other secret files
- Rotate any credential accidentally committed immediately
- JWT secrets must be strong random strings (minimum 32 characters)
- Database passwords must not match any default or example values in documentation
