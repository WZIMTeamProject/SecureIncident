# Database Migrations (Alembic)

## Generating Migrations

Always auto-generate migrations from model changes; never write raw DDL by hand unless Alembic can't express it.

```bash
# Generate migration after model change
alembic revision --autogenerate -m "add status column to incidents"

# Apply migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

## Migration File Rules

- **Always implement `downgrade()`** — every migration must be reversible. An empty `downgrade` is only acceptable if the operation is truly irreversible (e.g., dropping a table containing data).
- **One logical change per migration** — don't combine "add column" with "backfill data" in one file. Use two sequential migrations.
- **Never modify a committed migration file** — create a new migration to fix a mistake after it's been merged.
- **Review generated migrations** — Alembic's autogenerate misses some changes (default values, check constraints, enum changes). Always inspect the generated file before committing.

## Naming Convention

Migration file names must be descriptive (Alembic uses the `-m` message as the suffix):

```
# Good
0001_create_users_table.py
0002_add_status_to_incidents.py
0003_add_index_on_incident_project_id.py

# Bad
0001_auto.py
```

## Data Migrations

If you need to backfill data as part of a schema change:
1. Add the nullable column (schema migration)
2. Backfill existing rows (data migration — separate file)
3. Add `NOT NULL` constraint (schema migration — separate file)

This ensures each step is individually reversible and safe.

## Deployment Order

For columns with `NOT NULL` and no default: always deploy in phases on production — add nullable first, backfill, then constrain. For this project (early stage), applying `upgrade head` before starting the app is sufficient.

## Initial Migration

The first migration should create all tables from scratch (the full schema). Run `alembic revision --autogenerate -m "initial schema"` after all models are defined.
