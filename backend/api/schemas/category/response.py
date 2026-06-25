from uuid import UUID

from api.schemas.common.pagination import PaginatedResponse
from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None


CategoryListResponse = PaginatedResponse[CategoryResponse]
