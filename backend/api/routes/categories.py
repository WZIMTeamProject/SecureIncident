from fastapi import APIRouter, status
from api.schemas.common.base import CreatedIdResponse
from api.schemas.category.response import (
	CategoryResponse,
    CategoryListResponse
)
from api.schemas.category.request import  (
    CreateCategoryRequest,
    UpdateCategoryRequest
)
from uuid import UUID

router = APIRouter(prefix="/projects/{project_id}/categories", tags=["Categories"])

@router.get("", response_model=CategoryListResponse)
def get_categories(project_id: UUID):
    # TODO: logika pobierania kategorii
    categories = []
    return CategoryListResponse(categories=categories)

@router.post("", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_category(project_id: UUID, body: CreateCategoryRequest):
    # TODO: logika tworzenia kategorii
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")

@router.patch("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_category(project_id: UUID, category_id: UUID, body: UpdateCategoryRequest):
    # TODO: logika aktualizowania kategorii
    return
 
 
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(project_id: UUID, category_id: UUID):
    # TODO: logika usuwania kategorii
    return
