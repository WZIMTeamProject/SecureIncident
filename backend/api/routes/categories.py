from fastapi import APIRouter, status
from api.schemas.common.base import CreatedIdResponse
from api.schemas.category.response import (
	CategoryResponse,
    CategoryListResponse
)
from api.schemas.category.request import CreateCategoryRequest
from uuid import UUID

router = APIRouter(prefix="/projects/{project_id}/categories", tags=["Categories"])

@router.get("", response_model=CategoryListResponse)
def get_categories(project_id: UUID):
    # TODO: pobierz kategorie z bazy dla danego projektu
    categories = []
    return CategoryListResponse(categories=categories)

@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_category(project_id: UUID, body: CreateCategoryRequest):
    # TODO: utworz kategorie w bazie
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")