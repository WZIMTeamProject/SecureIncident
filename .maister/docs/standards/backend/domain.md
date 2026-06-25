# Domain Rules

These rules come from the product specification and must be enforced at the API/service layer.

## Users & Roles

- A user has **exactly one role per project** — one `UserProject` row per `(user_id, project_id)` pair
- A user can have different roles in different projects
- Roles are project-scoped, never global
- **Single-organization membership**: a user can belong to many projects, but only within **one** organization (or in private projects). This invariant is stated in the published OpenAPI contract description.

## Incidents

- An incident belongs to **exactly one project** and cannot be moved to a different project
- Four fields are mandatory at creation: `title`, `description`, `category`, `project`
- The **category** field is required at creation time — it is not optional
- Incidents cannot be deleted from the UI — they can only be resolved or closed

## Comments

- Comments on incidents are **immutable** — they cannot be edited after creation
- If a user wants to correct a comment, they add a new one
- Comments remain attached to an incident even after the assigned solver changes
