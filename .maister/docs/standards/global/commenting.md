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

Write a concise description for every function in the style of professional API documentation. Start with what the function does; add a second sentence or short paragraph when the contract is not obvious from the signature — permissions, domain rules, security behavior, atomicity, or one-time token semantics. Include information that was previously documented in comments rather than dropping it during refactors. Keep it readable, not exhaustive; never write multi-paragraph essays for internal helpers.

## JSDoc (TypeScript)

Prefer typed signatures over JSDoc. Add JSDoc for exported utilities and hooks when usage constraints are non-obvious — auth cookie behavior, dev-only bypasses, error mapping, or middleware contracts. One short description plus `@param` / `@returns` when they clarify behavior not visible from types.
