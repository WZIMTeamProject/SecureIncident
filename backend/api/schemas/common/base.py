from pydantic import BaseModel
from uuid import UUID


class CreatedIdResponse(BaseModel):
    id: UUID


class ErrorResponse(BaseModel):
    message: str