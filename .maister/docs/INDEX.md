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
SecureIncident's purpose and goals: a web-based incident reporting platform enabling organizations to manage, track, and resolve internal incidents with a full audit trail. Covers current state (early-stage MVP, ~3 weeks old), target users (team members and managers), and goals for the next 5-6 weeks (frontend integration, backend merge, AWS deployment, CI/CD, working MVP covering the full incident lifecycle).

#### Roadmap (`project/roadmap.md`)
Four-phase delivery plan within a 5-6 week timeline. Phase 1 (Weeks 1-2): merge backend branches, DB migration setup, frontend routing, backend-frontend connection, environment config. Phase 2 (Weeks 2-4): auth UI, incident management CRUD, project/org management, audit trail UI, testing suite. Phase 3 (Weeks 4-5): Docker/Compose, GitHub Actions CI/CD, AWS infrastructure, production config. Phase 4 (Weeks 5-6): documentation, QA, demo environment. Includes effort estimates (S/M/L) per task.

#### Technology Stack (`project/tech-stack.md`)
Full inventory of technology choices with rationale. Frontend: React 19, TypeScript (strict mode), React Router 7, Vite 8, Tailwind CSS 4. Backend: FastAPI 0.104.1, Uvicorn, Pydantic v2, SQLAlchemy 2.0, Alembic. Database: PostgreSQL (production) / MySQL (dev alternative) via SQLAlchemy. Auth: JWT with python-jose + PyJWT, bcrypt via passlib. API contract: OpenAPI 3.0.3 (schema-first). Infrastructure: Docker + Docker Compose (planned), GitHub Actions CI/CD (planned), AWS ECS/Fargate + RDS (target).

#### Architecture (`project/architecture.md`)
Monorepo client-server architecture — React SPA communicating with FastAPI REST backend via OpenAPI-defined contract. Describes frontend structure (`Frontend/`), backend layered architecture (`backend/api/routes`, `schemas`, `dependencies`), database ORM models (`backend/db/models/`), and API specification (`docs/api/`). Includes domain model (Organization → Projects → Incidents hierarchy, User/UserProject associations), data flow diagram (Browser → FastAPI JWT/RBAC → SQLAlchemy → PostgreSQL), and target AWS deployment topology (CloudFront+S3, ALB, ECS/Fargate, RDS).

---

## Technical Standards

### Global Standards

Located in `.maister/docs/standards/global/`

#### Coding Style (`standards/global/coding-style.md`)
TypeScript and Python naming conventions: `camelCase` for TS variables/functions, `PascalCase` for React components/types and Python classes, `snake_case` for Python variables/functions, `SCREAMING_SNAKE_CASE` for module-level constants. File organization: one primary export per file, feature/domain grouping (not type-based layers), files kept under ~300 lines. Formatting: 2-space indent for TS, 4-space for Python, 100-char line limit, single quotes in TypeScript, double quotes in Python.

#### Commenting (`standards/global/commenting.md`)
Write no comments by default — only add a comment when the WHY is non-obvious (hidden constraint, workaround for a specific bug, performance trade-off, security invariant). Never comment what the code does, current PR context, or caller lists. Docstrings only when a function's contract isn't derivable from its signature; JSDoc only for public utility functions with non-obvious usage constraints.

#### Conventions (`standards/global/conventions.md`)
Git workflow: `feature/<name>`, `fix/<name>`, `chore/<name>` branch naming; imperative present-tense commit messages; one concern per commit; no direct commits to `main`. Environment variables: never commit secrets; maintain `.env.example`; prefix frontend vars with `VITE_`; fail fast on missing required vars. Code review: author provides context; reviewer checks correctness, security, auth/permissions, test coverage; small focused PRs.

#### Error Handling (`standards/global/error-handling.md`)
Handle errors at system boundaries only (user input, external APIs, DB calls). Backend: use `HTTPException` with specific status codes; register global handlers in `main.py` for domain exceptions; never expose stack traces or SQL errors to clients; catch `SQLAlchemyError` and roll back at the service/route layer. Frontend: handle API errors in hooks/services, not components; show actionable user-facing messages; map 422 errors to form fields; never silently swallow errors.

#### Minimal Implementation (`standards/global/minimal-implementation.md`)
Build only what is needed right now — YAGNI strictly applied. A bug fix does not need surrounding cleanup; three similar lines is better than a premature abstraction; no half-finished skeleton features. Avoid: empty placeholder methods, speculative factories/strategies/adapters, generic utilities built for hypothetical future use, feature flags for single-case behavior. Delete exploration artifacts, commented-out code, unused imports, and dead branches promptly. Refactor only when solving a concrete problem, in a separate PR.

#### Validation (`standards/global/validation.md`)
Backend always validates; client-side is UX-only, not a security boundary. Use Pydantic v2 `Field` constraints and `@field_validator` on request schemas — FastAPI returns 422 with field-level errors automatically. Business rule validation (membership, cross-resource ownership) raises `HTTPException` at the route/service layer. Frontend: controlled form state, map 422 responses to field errors by name, show feedback on blur not on every keystroke. Security: never trust user-supplied IDs without authorization checks; use allowlists for enum-like fields; strip/trim string inputs before storing.

---

### Frontend Standards

Located in `.maister/docs/standards/frontend/`

#### Components (`standards/frontend/components.md`)
Always use functional components with hooks — no class components. Props defined with `<ComponentName>Props` interface, destructured in the function signature, kept to 6-8 max. Event handlers use `handle` prefix; boolean props use `is`/`has` prefix. State kept close to usage; use `useState` for local UI, `useReducer` for complex form state, React Query for server data. Custom hooks in a co-located `hooks/` directory. Use `useEffect` sparingly — prefer event handlers and React Query; always provide a dependency array.

#### CSS (`standards/frontend/css.md`)
Tailwind CSS v4 utility classes as the primary approach — no custom CSS unless utilities genuinely cannot express the design. Class order within elements: layout → positioning → box model → typography → visual → interactive → responsive prefixes. Use CSS custom properties from `index.css` for design tokens (light/dark theme support via CSS variables). Conditional class composition via `clsx`/`tailwind-merge` (`cn()` pattern). Custom CSS only in `index.css` (global) or co-located `.module.css` files; no inline `style` props for static values; no `!important`.

#### Accessibility (`standards/frontend/accessibility.md`)
Semantic HTML first — every clickable element must be a `<button>` or `<a href>`, never a `<div>` with `onClick`. All form inputs require an associated `<label>`. Keyboard navigation: all interactive elements reachable via Tab/Enter/Space; modals trap focus while open and restore it on close; never remove focus outlines. Color contrast: 4.5:1 minimum for normal text (WCAG AA). ARIA only when semantic HTML isn't sufficient: `aria-expanded`, `role="alert"`, `aria-live="polite"`, `aria-label` for repeated elements; decorative SVGs use `aria-hidden="true"`.

#### Responsive Design (`standards/frontend/responsive.md`)
Mobile-first with Tailwind breakpoints: base styles for mobile, then `sm:` (640px), `md:` (768px), `lg:` (1024px), `xl:` (1280px). Use `flex`/`grid` for layouts, `gap-*` over `margin` for spacing, `max-w-*` with `mx-auto` to constrain content width. Touch targets minimum 44x44px (`min-h-11 min-w-11`). Typography in `rem` units only (`text-base` minimum on mobile). Verify every feature at 375px, 768px, and 1280px viewports before marking done.

---

### Backend Standards

Located in `.maister/docs/standards/backend/`

#### API Design (`standards/backend/api.md`)
RESTful URLs with plural noun resources (`/projects`, `/incidents`); max 2 levels of nesting; query parameters for filtering/sorting/pagination. Correct HTTP method semantics (GET/POST/PUT/PATCH/DELETE). Consistent status codes: 201 for creation, 204 for no-content, 400/401/403/404/409 for client errors. Every endpoint has explicit Pydantic `request_model` and `response_model` — never return raw SQLAlchemy instances. Auth: every endpoint requires `Depends(get_current_user)` except `POST /auth/register` and `POST /auth/login`; check membership/role after confirming identity. List endpoints return paginated `PaginatedResponse[T]` with default limit 20, max 100.

#### Models (`standards/backend/models.md`)
SQLAlchemy 2.0 declarative style with `DeclarativeBase`, `Mapped`, and `mapped_column` for fully typed columns. Required on every model: `id` (UUID primary key, `default=uuid.uuid4`), `created_at` (server_default), `updated_at` (server_default + onupdate). Uses `sqlalchemy.dialects.postgresql.UUID(as_uuid=True)` — not integer autoincrement. Naming: `PascalCase` class (singular), `snake_case` table name (plural), `<related_model>_id` for foreign key columns. Enforce constraints at DB level: `nullable=False`, `unique=True`, `ForeignKey` with explicit `ondelete`. Index all foreign key columns and frequent `WHERE` clause columns. Relationships require `back_populates` on both sides; use `lazy="selectin"` or explicit `joinedload` in async contexts.

#### Migrations (`standards/backend/migrations.md`)
Auto-generate migrations with `alembic revision --autogenerate` — never write raw DDL by hand. Always implement `downgrade()`. One logical change per migration file — don't combine schema changes with data backfills. Never modify a committed migration file; create a new one to fix mistakes. Review generated files before committing (Alembic misses default values, check constraints, enum changes). Data migrations: add nullable column → backfill (separate file) → add NOT NULL (separate file). Descriptive migration names via the `-m` flag.

#### Queries (`standards/backend/queries.md`)
Use async session via `Depends(get_db)` — never create sessions manually in route handlers. Single-row queries use `scalar_one_or_none()` with explicit `None` handling. Eager-load relationships with `selectinload` (separate IN query) or `joinedload` (JOIN) whenever related data will be accessed — never access relationship attributes in a loop without prior eager loading (N+1 prevention). Write operations: `db.add()` → `await db.commit()` → `await db.refresh()`. Never interpolate user input into SQL strings; always use SQLAlchemy ORM or `text()` with `bindparam`.

---

### Testing Standards

Located in `.maister/docs/standards/testing/`

#### Test Writing (`standards/testing/test-writing.md`)
Test behavior not implementation — tests must survive refactoring. Descriptive names following `test_<scenario>_<expected_result>` format (e.g., `test_create_incident_returns_403_when_user_not_project_member`). Integration tests use `pytest-asyncio` + `httpx.AsyncClient` against the actual FastAPI app and a real test database (no DB mocking). Fixtures in `conftest.py`: `db`, `client`, `test_user`, `auth_headers`, `test_project`. Test coverage matrix: happy path, unauthenticated (401), unauthorized (403), validation errors (422), not found (404), business rule violations (409). Do not test framework behavior, trivial getters/setters, or third-party library internals.

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
