from pydantic import BaseModel
from typing import Optional

class CreateCategoryRequest(BaseModel):
    name: str

class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = None