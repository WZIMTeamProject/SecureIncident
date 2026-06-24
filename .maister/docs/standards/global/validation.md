# Validation

## Where to Validate

- **Backend always** — client-side validation is UX, not security. The backend must validate all input independently.
- **Frontend for immediate feedback** — validate on blur/submit to help users, but never rely on it as the only check.
- **At boundaries only** — validate at entry points (API endpoints, form submissions). Don't re-validate data that's already been validated and passed through internal layers.

## Backend Validation with Pydantic (FastAPI)

FastAPI validates all request bodies, query parameters, and path parameters automatically via Pydantic schemas. Define schemas precisely:

```python
from pydantic import BaseModel, Field, field_validator

class CreateIncidentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    category_id: int = Field(gt=0)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip()
```

FastAPI returns HTTP 422 with field-level errors automatically — don't duplicate this with manual checks unless business logic requires it.

## Whitespace Stripping via ConfigDict

Pydantic v2 request schemas set `model_config = ConfigDict(str_strip_whitespace=True)` so all string inputs are trimmed automatically — this is the concrete mechanism behind the "strip/trim string inputs" rule in the Security section below. Pair it with `Field()` constraints and `@field_validator` + `@classmethod` for business validation.

```python
from pydantic import BaseModel, ConfigDict, Field

class CreateProjectRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
```

## Business Rule Validation

Validate business constraints in the route handler or a service function, raising `HTTPException` with an appropriate status code. Examples:
- User is a member of the project before allowing incident creation
- Category belongs to the same project as the incident
- A user cannot assign an incident to someone outside the project

## Frontend Validation

- Use controlled form state with error messages next to each field
- Map 422 responses from the backend to form field errors by field name
- Show validation feedback on blur (not on every keystroke) for better UX
- Required fields, min/max lengths, and format checks (email, date) can be validated client-side for immediacy

## Security

- Never trust user-supplied IDs without checking authorization (fetch the resource and verify ownership/membership)
- Use allowlists for enum-like fields; don't try to blocklist invalid values
- Strip and trim string inputs before storing — leading/trailing whitespace in titles is almost always unintentional
