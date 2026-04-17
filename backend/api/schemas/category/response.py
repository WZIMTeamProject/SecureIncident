from pydantic import BaseModel
from typing import List
from uuid import UUID


class CategoryResponse(BaseModel):
    id: UUID
    name: str


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]