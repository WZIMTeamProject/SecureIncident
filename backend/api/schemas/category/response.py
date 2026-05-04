from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]