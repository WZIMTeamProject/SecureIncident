# Logging (Backend)

## Module-Level Logger

Declare a logger at the top of every service and module file — never inside functions:

```python
import logging

logger = logging.getLogger(__name__)
```

## Structured Key=Value Format

Log messages use a structured `key=value` format (not JSON, but machine-parseable). Values are passed as `%s` arguments, not f-strings:

```python
# Correct
logger.info(
    "Incident created incident_id=%s project_id=%s user_id=%s",
    incident.id, project_id, current_user.id,
)
logger.warning(
    "Incident access denied: user not project member project_id=%s user_id=%s",
    project_id, user_id,
)

# Avoid — f-string formatting (eager, not lazy)
logger.info(f"Incident created incident_id={incident.id}")
```

## Log Level Conventions

| Level | When to use |
|-------|-------------|
| `logger.warning(...)` | Before raising an `HTTPException` (client error) |
| `logger.info(...)` | After a successful mutation |
| `logger.error(...)` | Unexpected server-side failures |
| `logger.debug(...)` | Verbose diagnostic info (dev only) |

```python
# Pattern: warn before raise, info after success
async def assign_solver(db, incident_id, solver_id, current_user):
    incident = await _get_incident_or_404(db, incident_id)
    membership = await repositories.project_repo.get_membership(db, incident.project_id, current_user.id)
    if membership is None:
        logger.warning("Assign solver denied: not a member project_id=%s user_id=%s", incident.project_id, current_user.id)
        raise HTTPException(status_code=403, detail="Not a project member")

    incident.solver_id = solver_id
    await db.commit()
    logger.info("Solver assigned incident_id=%s solver_id=%s", incident_id, solver_id)
```

## Centralized Configuration

Logging is fully configured in `main.py` using `logging.config.dictConfig()` with a `LOGGING_CONFIG` dictionary. Do not call `logging.basicConfig()` in any other file.

A `LoggingMiddleware` injects a per-request UUID into a `ContextVar`, and a `RequestIDFilter` attaches it to every log record as `request_id`. The log format includes `[%(request_id)s]`.

Log format is switchable between human-readable and JSON via the `LOG_FORMAT` config setting (uses `pythonjsonlogger` for JSON output).

## What Not to Log

Never log passwords, tokens, JWT payloads, or full request bodies. Log IDs and operation context only.
