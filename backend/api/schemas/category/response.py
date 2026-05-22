from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from api.schemas.common.pagination import PaginatedResponse


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None


CategoryListResponse = PaginatedResponse[CategoryResponse]
