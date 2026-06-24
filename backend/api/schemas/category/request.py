from pydantic import BaseModel, ConfigDict, Field


class CreateCategoryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=2000)


class UpdateCategoryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=50)
