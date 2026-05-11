# Commenting

## Core Rule
Write no comments by default. Only add a comment when the **WHY** is non-obvious: a hidden constraint, a subtle invariant, a workaround for a specific bug, or behavior that would surprise a reader. If removing a comment wouldn't confuse a future developer, don't write it.

## What Not to Comment

- **What the code does** — well-named identifiers already do this. `# fetch user by id` above `get_user(user_id)` is noise.
- **Current task or PR context** — "added for the incident assignment flow" belongs in the PR description and rots as code evolves.
- **Callers** — "used by IncidentService" is a maintenance liability; use IDE navigation instead.
- **Obvious logic** — `i += 1  # increment counter` is never helpful.

## What to Comment

- A non-obvious business rule: `# users without an org can only access private projects`
- A workaround for a known bug/limitation: `# SQLAlchemy lazy-load fails in async context, explicit join required`
- A performance trade-off that isn't obvious from the code.
- A security invariant that must not be changed: `# constant-time comparison to prevent timing attacks`

## Docstrings (Python)

Skip docstrings on trivial functions. Only add one when the function's contract isn't derivable from its signature — complex preconditions, non-obvious side effects, or public API intended for external consumers. Keep it one line when possible; never write multi-paragraph docstrings for internal code.

## JSDoc (TypeScript)

Prefer typed signatures over JSDoc. Only add JSDoc for public utility functions or hooks that have non-obvious usage constraints.
