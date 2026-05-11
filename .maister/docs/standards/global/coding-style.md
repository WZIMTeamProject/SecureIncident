# Coding Style

## Naming Conventions

### General Rules
Use descriptive names that reveal intent. Avoid abbreviations unless universally understood (`id`, `url`, `jwt`, `api`). Boolean variables and functions start with a verb: `isLoading`, `hasPermission`, `canEdit`. Functions use verb phrases: `createIncident`, `fetchProjects`, `validateToken`.

### TypeScript / JavaScript
- Variables and functions: `camelCase`
- React components, types, interfaces: `PascalCase`
- Module-level immutable constants: `SCREAMING_SNAKE_CASE`
- Component files: `PascalCase` (`IncidentForm.tsx`, `ProjectList.tsx`)
- All other files: `camelCase` (`apiClient.ts`, `useAuth.ts`, `incidentService.ts`)
- Interfaces: no `I` prefix — prefer `User` over `IUser`

### Python
- Variables, functions, modules: `snake_case`
- Classes (models, schemas, exceptions): `PascalCase`
- Module-level constants: `SCREAMING_SNAKE_CASE`
- Private helpers: single leading underscore (`_build_query`)
- File names: `snake_case` (`incident_service.py`, `auth_router.py`)

## File Organization

- One primary export per file — one component per `.tsx` file, one SQLAlchemy model per `.py` file.
- Group files by **feature/domain**, not by type. Prefer `incidents/` containing routes, schemas, and service over separate `routes/`, `schemas/`, `services/` directories per layer.
- Keep files under ~300 lines. If a file grows larger, split by responsibility.
- Remove all unused imports before committing.

## Formatting

- TypeScript/JavaScript: 2-space indentation, max 100-char lines.
- Python: 4-space indentation, max 100-char lines.
- No trailing whitespace. Single blank line at end of file.
- Consistent quote style: single quotes in TypeScript, double quotes in Python strings.
