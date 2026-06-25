# Security

## JWT

Use **PyJWT 2.13+** for JWT token generation and validation. `python-jose` was explicitly removed due to known CVEs — do not re-introduce it.

## Passwords

Passwords must meet all of these requirements (enforced at `@field_validator` level in the registration schema):

- Minimum 8 characters
- At least one lowercase letter
- At least one uppercase letter
- At least one digit
- At least one special character

Use `bcrypt` via `passlib` for hashing. Never store or log plaintext passwords.

## Error Messages

API error messages must not reveal internal implementation details, database schema, or stack traces. Technical errors go to server logs; clients receive a generic message:

```python
# Correct
raise HTTPException(status_code=401, detail="Invalid credentials")

# Avoid — reveals which field was wrong (username enumeration risk)
raise HTTPException(status_code=401, detail="Username does not exist")
```

## User Content — Plain Text Only

Comments, descriptions, titles, and other user-submitted text fields must be stored and rendered as plain text. Do not allow HTML in user content. This prevents XSS attacks. Strip whitespace via `ConfigDict(str_strip_whitespace=True)` on request schemas.

## Audit Trail

The incident change history (`AuditLog` table) must be **immutable from the UI**. Audit events that must be recorded per incident:

- Comment added
- Status changed
- Assigned solver changed

System-level events that must be logged:
- Successful login
- Failed login attempt
- Role/permission changes
- Admin operations on organizations and projects

## Non-Root Container

The backend Docker container runs as a dedicated non-root user (`appuser`). Do not change this — running as root in a container is a security risk.

## Automated Security Scanning

Backend code is scanned by **bandit** (SAST, configured via `[tool.bandit]` in `pyproject.toml`, excluding `backend/tests`) and dependencies are audited by **pip-audit**. Both run as **pre-commit hooks** and in **CI** (alongside the existing vulture dead-code detection). Findings must be resolved before merge.

## Password Reset Behavioral Contract

The password-reset request and confirm endpoints **always return 204**, regardless of whether the account exists or whether the email was actually sent — this prevents account enumeration. The email is dispatched via an async background task so the request stays non-blocking.

- Reset tokens expire after **30 minutes**.
- Requesting a new reset **invalidates any pending token** for that account.
- Change-password and reset-password deliberately **do NOT invalidate active sessions** — an already-issued JWT keeps working until it expires.
