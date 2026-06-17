from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class CreateCategoryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=2000)


class UpdateCategoryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(None, min_length=1, max_length=50)