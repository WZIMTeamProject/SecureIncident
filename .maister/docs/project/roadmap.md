# Development Roadmap

## Current State
- **Version**: 0.1.1 (API spec)
- **Key Features**: API specification (OpenAPI), database models, frontend scaffold, JWT auth design
- **Recent Updates**: Frontend scaffold merged, API specification merged (April 2026)

## Phase 1: Integration & Foundation (Weeks 1-2)

- [ ] **Merge backend branches** — Merge `backend_api` and `database_models` into `main` `[Effort: S]`
- [ ] **Database initialization** — Set up Alembic migration scripts, initial DB seeding `[Effort: S]`
- [ ] **Frontend routing & pages** — Implement login, dashboard, incident list/detail views `[Effort: M]`
- [ ] **Backend-frontend connection** — Configure CORS, API base URL, auth token flow `[Effort: S]`
- [ ] **Environment configuration** — Create `.env.example`, document setup steps in README `[Effort: S]`

## Phase 2: Core Features (Weeks 2-4)

- [ ] **Authentication UI** — Login and register pages with JWT token handling `[Effort: M]`
- [ ] **Incident management** — Create, view, update, and assign incidents `[Effort: L]`
- [ ] **Project & organization management** — Create projects, manage members and roles `[Effort: M]`
- [ ] **Categories & roles** — Category and role management within projects `[Effort: S]`
- [ ] **Audit trail UI** — Display IncidentLog history per incident `[Effort: S]`
- [ ] **Testing suite** — Backend pytest coverage, frontend unit tests `[Effort: M]`

## Phase 3: AWS Deployment (Weeks 4-5)

- [ ] **Docker & Docker Compose** — Containerize backend and frontend for consistent deployments `[Effort: M]`
- [ ] **CI/CD pipeline** — GitHub Actions for testing, linting, build, and deploy `[Effort: M]`
- [ ] **AWS infrastructure** — Deploy to AWS (ECS/Fargate or EC2 + RDS) `[Effort: L]`
- [ ] **Production configuration** — Secrets management, environment variables, HTTPS `[Effort: S]`

## Phase 4: Polish & Handoff (Weeks 5-6)

- [ ] **README & documentation** — Complete setup guide, architecture overview, contribution guide `[Effort: S]`
- [ ] **Bug fixes & QA** — Final verification pass by testing team (3 testers) `[Effort: M]`
- [ ] **Demo environment** — Stable working demo on AWS for project presentation `[Effort: S]`

## Future Considerations
- **Feature Ideas**: Email notifications, incident severity levels, SLA tracking, analytics dashboard
- **Scalability**: Caching layer, query optimization, load balancing

---
**Effort Scale**: `S`: 2-3 days | `M`: 1 week | `L`: 2+ weeks
