# Documentation Index

**IMPORTANT**: Read this file at the beginning of any development task to understand available documentation and standards.

## Quick Reference

### Project Documentation
Project-level documentation covering vision, goals, architecture, and technology choices.

### Technical Standards
Coding standards, conventions, and best practices organized by domain.

---

## Project Documentation

Located in `.maister/docs/project/`

#### Vision (`project/vision.md`)
SecureIncident's purpose and goals: a web-based incident reporting platform enabling organizations to manage, track, and resolve internal incidents with a full audit trail. Covers current state (early-stage MVP, ~3 weeks old), target users (team members and managers within organizations), and goals targeting the hard deadline June 18, 2026 (frontend integration, backend merge, AWS deployment, CI/CD, working MVP covering the full incident lifecycle).

#### Roadmap (`project/roadmap.md`)
Four-phase delivery plan time-boxed to the hard deadline of June 18, 2026. Phase 1 (June 9–11): merge backend branches, DB migration setup, frontend routing, backend-frontend connection, environment config. Phase 2 (June 11–15): auth UI, incident management CRUD, project/org management, audit trail UI, testing suite. Phase 3 (June 15–17): Docker/Compose, GitHub Actions CI/CD, AWS infrastructure, production config. Phase 4 (June 17–18): documentation, QA, demo environment. Includes effort estimates (S/M/L) per task.

#### Technology Stack (`project/tech-stack.md`)
Full inventory of technology choices with rationale. Frontend: React 19, TypeScript (strict mode), React Router 7, Vite 8, Tailwind CSS 4. Backend: FastAPI 0.136+, Uvicorn 0.49+, Pydantic v2 2.13+, pydantic-settings, SQLAlchemy 2.0.50+, Alembic 1.18+. Database: PostgreSQL-only via asyncpg (MySQL dropped). Auth: PyJWT 2.13+ only (python-jose removed due to CVE), bcrypt 5+ via passlib. Package management: uv + pyproject.toml. API contract: OpenAPI 3.0.3 (schema-first). Infrastructure: Docker + Docker Compose (planned), GitHub Actions CI/CD (planned), AWS EC2 + RDS (target).

#### Architecture (`project/architecture.md`)
Monorepo client-server architecture — React SPA communicating with FastAPI REST backend via OpenAPI-defined contract. Describes frontend structure (`Frontend/`), backend layered architecture (`backend/api/routes`, `schemas`, `dependencies`), database ORM models (`backend/db/models/`), and API specification (`docs/api/`). Includes domain model (Organization → Projects → Incidents hierarchy, User/UserProject associations), data flow diagram (Browser → FastAPI JWT/RBAC → SQLAlchemy → PostgreSQL), and target AWS deployment topology (CloudFront+S3, ALB, EC2, RDS).

---

## Technical Standards

### Global Standards

Located in `.maister/docs/standards/global/`

#### Coding Style (`standards/global/coding-style.md`)
TypeScript and Python naming conventions: `camelCase` for TS variables/functions, `PascalCase` for React components/types and Python classes, `snake_case` for Python variables/functions/modules, `SCREAMING_SNAKE_CASE` for module-level constants. File organization: one primary export per file, feature/domain grouping (not type-based layers), files kept under ~300 lines. Formatting: 2-space indent for TS (100-char limit), 4-space for Python (88-char limit enforced by ruff), single quotes in TypeScript, double quotes in Python. Also covers TypeScript import conventions (relative paths with file extensions, no `@/` alias) and the form field constants pattern (exported `SCREAMING_SNAKE_CASE` constants in co-located `forms.ts` files).

#### Commenting (`standards/global/commenting.md`)
Write no comments by default — only add a comment when the WHY is non-obvious (hidden constraint, workaround for a specific bug, performance trade-off, security invariant). Never comment what the code does, current PR context, or caller lists. Docstrings only when a function's contract isn't derivable from its signature; JSDoc only for public utility functions with non-obvious usage constraints.

#### Conventions (`standards/global/conventions.md`)
Git workflow: `feature/<name>`, `fix/<name>`, `chore/<name>` branch naming; imperative present-tense commit messages; one concern per commit; no direct commits to `main`. Environment variables: never commit secrets; maintain `.env.example`; prefix frontend vars with `VITE_`; fail fast on missing required vars. Dependency management: add only when solving a real current problem, remove unused promptly. Code review: author provides context; reviewer checks correctness, security, auth/permissions, test coverage; small focused PRs.

#### Error Handling (`standards/global/error-handling.md`)
Handle errors at system boundaries only (user input, external APIs, DB calls). Backend: use `HTTPException` with specific status codes; register global handlers in `main.py` for domain exceptions; never expose stack traces or SQL errors to clients; catch `SQLAlchemyError` and roll back at the service/route layer. Frontend: handle API errors in hooks/services not components; use `fetcher.data?.error` pattern with React Router's `useFetcher`; show actionable user-facing messages; map 422 errors to form fields; never silently swallow errors with an empty `catch {}`.

#### Minimal Implementation (`standards/global/minimal-implementation.md`)
Build only what is needed right now — YAGNI strictly applied. A bug fix does not need surrounding cleanup; three similar lines is better than a premature abstraction; no half-finished skeleton features. Avoid: empty placeholder methods, speculative factories/strategies/adapters, generic utilities built for hypothetical future use, feature flags for single-case behavior. Delete exploration artifacts, commented-out code, unused imports, and dead branches promptly. Refactor only when solving a concrete problem, in a separate PR.

#### Tooling (`standards/global/tooling.md`)
Pre-commit hook configuration covering all auto-fixable checks: `trailing-whitespace`, `end-of-file-fixer`, `check-merge-conflict`, `ruff --fix` + `ruff-format` for Python (E/F/I/UP rules, 88-char lines, double quotes), `vulture` for dead code detection at ≥80% confidence, and `eslint --fix` for TypeScript/TSX. Also documents CI-specific conventions (`npm ci` over `npm install`, `docker compose --build` after migration changes) and the Alembic `upgrade head` requirement before starting the backend server.

#### Validation (`standards/global/validation.md`)
Backend always validates; client-side is UX-only, not a security boundary. Use Pydantic v2 `Field` constraints and `@field_validator` on request schemas — FastAPI returns 422 with field-level errors automatically. Business rule validation (membership, cross-resource ownership) raises `HTTPException` at the route/service layer. Frontend: controlled form state, map 422 responses to field errors by field name, show feedback on blur not on every keystroke. Security: never trust user-supplied IDs without authorization checks; use allowlists for enum-like fields; strip/trim string inputs before storing.

---

### Frontend Standards

Located in `.maister/docs/standards/frontend/`

#### Accessibility (`standards/frontend/accessibility.md`)
Semantic HTML first — every clickable element must be a `<button>` or `<a href>`, never a `<div>` with `onClick`. All form inputs require an associated `<label>`. Keyboard navigation: all interactive elements reachable via Tab/Enter/Space; modals trap focus while open and restore it on close; never remove focus outlines. Color contrast: 4.5:1 minimum for normal text (WCAG AA); never use color as the only means of conveying information. ARIA only when semantic HTML isn't sufficient: `aria-expanded`, `role="alert"`, `aria-live="polite"`, `aria-label` for repeated elements; decorative SVGs use `aria-hidden="true"`.

#### Components (`standards/frontend/components.md`)
Always use functional components with hooks — no class components. Page-level components use `SI` prefix + PascalCase (`SILoginPage`, `SIDashboard`); shared components use plain PascalCase. Props defined with `<ComponentName>Props` interface, destructured in the function signature, kept to 6-8 max. Form submission uses React Router's `useFetcher` (not controlled state + `useEffect`). State kept close to usage: `useState` for local UI, `useReducer` for complex form state; server data stays in React Query or custom hooks. Custom hooks in a co-located `hooks/` directory; `useEffect` used sparingly with a dependency array always provided.

#### CSS (`standards/frontend/css.md`)
Tailwind CSS v4 utility classes as the primary approach — no custom CSS unless utilities genuinely cannot express the design. All themed colors use project-specific CSS custom properties (`var(--color-si-*)`) via Tailwind's arbitrary value syntax — never Tailwind palette names or hardcoded hex values. Class order within elements: layout → positioning → box model → typography → visual → interactive → responsive prefixes. Conditional class composition via `clsx`/`tailwind-merge` (`cn()` pattern). Custom CSS only in `index.css` (global) or co-located `.module.css` files; no inline `style` props for static values; no `!important`.

#### Responsive Design (`standards/frontend/responsive.md`)
Mobile-first with Tailwind breakpoints: base styles for mobile, then `sm:` (640px), `md:` (768px), `lg:` (1024px), `xl:` (1280px). Use `flex`/`grid` for layouts, `gap-*` over `margin` for spacing, `max-w-*` with `mx-auto` to constrain content width. Touch targets minimum 44x44px (`min-h-11 min-w-11`). Typography in `rem` units only (`text-base` minimum on mobile). Verify every feature at 375px, 768px, and 1280px viewports before marking done.

---

### Backend Standards

Located in `.maister/docs/standards/backend/`

#### API Design (`standards/backend/api.md`)
RESTful URLs with plural noun resources (`/projects`, `/incidents`); max 2 levels of nesting; query parameters for filtering/sorting/pagination. HTTP method semantics: POST returns 201 + `CreatedIdResponse`, PATCH/DELETE return 204. Schema organization: Pydantic schemas in `api/schemas/<domain>/request.py` and `response.py` — no monolithic schema files, never return raw SQLAlchemy instances. Route handlers contain zero business logic — they delegate to service functions. Auth: every endpoint requires `Depends(get_current_user)` except `POST /auth/register` and `POST /auth/login`; guard helpers (`_get_incident_or_404`, `_get_membership_or_403`) centralize 404/403 logic. List endpoints return paginated `PaginatedResponse[T]` with default limit 20, max 100.

#### Domain Rules (`standards/backend/domain.md`)
Business rules from the product specification that must be enforced at the API/service layer. Users: exactly one role per project (one `UserProject` row per `(user_id, project_id)` pair); roles are project-scoped, never global. Incidents: belong to exactly one project and cannot be moved; four fields mandatory at creation (title, description, category, project); cannot be deleted from the UI — only resolved or closed. Comments: immutable after creation; users add a new comment to correct an earlier one.

#### Logging (`standards/backend/logging.md`)
Module-level logger declared at the top of every service file using `logging.getLogger(__name__)` — never inside functions. Structured `key=value` log format with `%s` arguments (not f-strings) for lazy evaluation. Log level conventions: `warning` before raising an `HTTPException`, `info` after a successful mutation, `error` for unexpected server failures, `debug` for verbose dev diagnostics. Logging fully configured in `main.py` via `logging.config.dictConfig()` — no `logging.basicConfig()` in other files. `LoggingMiddleware` injects a per-request UUID into every log record via `ContextVar`. Never log passwords, tokens, JWT payloads, or full request bodies.

#### Migrations (`standards/backend/migrations.md`)
Auto-generate migrations with `alembic revision --autogenerate` — never write raw DDL by hand. Always implement `downgrade()`. One logical change per migration file — don't combine schema changes with data backfills. Never modify a committed migration file; create a new one to fix mistakes. Review generated files before committing (Alembic misses default values, check constraints, enum changes). Data migrations: add nullable column → backfill (separate file) → add NOT NULL (separate file). Descriptive migration names via the `-m` flag (e.g., `add_status_column_to_incidents`).

#### Models (`standards/backend/models.md`)
SQLAlchemy 2.0 declarative style with `DeclarativeBase`, `Mapped`, and `mapped_column` for fully typed columns. Required on every model: `id` (UUID primary key, `default=uuid.uuid4`), `created_at` (server_default), `updated_at` (server_default + onupdate). Uses `sqlalchemy.dialects.postgresql.UUID(as_uuid=True)` — not integer autoincrement. Naming: `PascalCase` class (singular), `snake_case` table name (plural), `<related_model>_id` for foreign key columns. Enforce constraints at DB level: `nullable=False`, `unique=True`, `ForeignKey` with explicit `ondelete`. Index all foreign key columns and frequent `WHERE` clause columns. Relationships require `back_populates` on both sides; use `lazy="selectin"` or explicit `joinedload` in async contexts.

#### Queries (`standards/backend/queries.md`)
Use async session via `Depends(get_db)` — never create sessions manually in route handlers. All database access goes through repository functions in `db/repositories/<model>_repo.py`; services never issue SQLAlchemy queries directly. Flush/commit split: repositories call `db.add()` + `await db.flush()` (no commit); services call `await db.commit()` after all repository calls to ensure atomicity. Single-row queries use `scalar_one_or_none()` with explicit `None` handling. Eager-load relationships with `selectinload` or `joinedload` whenever related data will be accessed — never access relationship attributes in a loop without prior eager loading (N+1 prevention). Never interpolate user input into SQL strings; always use SQLAlchemy ORM or `text()` with `bindparam`.

#### Security (`standards/backend/security.md`)
JWT: use PyJWT 2.13+ only — `python-jose` was removed due to CVEs and must not be re-introduced. Password requirements enforced at `@field_validator` level: minimum 8 characters with lowercase, uppercase, digit, and special character; hash with bcrypt via passlib, never store or log plaintext. API error messages must not reveal internal details (no username enumeration, no stack traces). User content (comments, descriptions, titles) stored and rendered as plain text only — no HTML allowed (XSS prevention). Audit trail (`AuditLog`) is immutable from the UI; records comment additions, status changes, solver changes, login events, and admin operations. Backend Docker container runs as a non-root `appuser`.

---

### Testing Standards

Located in `.maister/docs/standards/testing/`

#### Test Writing (`standards/testing/test-writing.md`)
Test behavior not implementation — tests must survive refactoring. Tests grouped into `Test<Feature>` classes; methods follow `test_<scenario>_<expected_result>` format (e.g., `test_create_incident_returns_403_when_user_not_project_member`). Integration tests use `pytest-asyncio` (auto mode, no decorator needed) + `httpx.AsyncClient` against the actual FastAPI app and a real test database (no DB mocking). Fixtures use `db.add()` + `await db.flush()` (never `commit`) inside savepoint-wrapped transactions that roll back after each test. Coverage matrix: happy path, unauthenticated (401), unauthorized (403), validation errors (422), not found (404), business rule violations (409). Do not test framework behavior, trivial getters/setters, or third-party library internals.

---

### Infrastructure Standards

Located in `.maister/docs/standards/infrastructure/`

#### CI/CD Pipeline (`standards/infrastructure/ci-cd.md`)
Both pipelines (backend and frontend) trigger only on pushes to `main` — feature branches do not trigger any automated build or deploy. Backend pipeline: spin up PostgreSQL 16 service container, run `pytest` against a real database (tests must pass before building), build and push Docker image to GHCR with `:latest` and `:<github.sha>` tags, deploy to EC2 via SSH, verify with `GET /health` returning 2xx. Frontend pipeline: `npm ci`, build Docker image with `VITE_API_BASE_URL` injected as a build argument (never hardcoded), push to GHCR, deploy to EC2. The `/health` endpoint must exist on port 8000, require no authentication, and respond within the Docker healthcheck timeout.

---

## How to Use This Documentation

1. **Start Here**: Always read this INDEX.md first to understand what documentation exists
2. **Project Context**: Read relevant project documentation before starting work
3. **Standards**: Reference appropriate standards when writing code
4. **Keep Updated**: Update documentation when making significant changes
5. **Customize**: Adapt all documentation to your project's specific needs

## Updating Documentation

- Project documentation should be updated when goals, tech stack, or architecture changes
- Technical standards should be updated when team conventions evolve
- Always update INDEX.md when adding, removing, or significantly changing documentation
