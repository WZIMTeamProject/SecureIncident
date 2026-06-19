from pydantic import BaseModel
from uuid import UUID


class CreatedIdResponse(BaseModel):
    id: UUID


class ErrorResponse(BaseModel):
    message: str


class DetailResponse(BaseModel):
    """Standard error body returned by FastAPI's HTTPException ({"detail": "..."})."""
    detail: str
 