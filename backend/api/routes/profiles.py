from fastapi import APIRouter, status
from uuid import UUID

from api.schemas.profiles.request import UpdateProfileRequest
from api.schemas.profiles.response import (
    ProfileResponse,
    UserSearchResponse,
    UserSearchResult
)

router = APIRouter(tags=["Profiles"])

@router.get("/profiles/me", response_model=ProfileResponse)
def get_my_profile():
    # TODO: pobierz profil zalogowanego u¿ytkownika
    return ProfileResponse(
        id="00000000-0000-0000-0000-000000000000",
        username="test_user",
        bio=None,
        profilePictureUrl=None,
    )
 
 
@router.patch("/profiles/me", status_code=status.HTTP_204_NO_CONTENT)
def update_my_profile(body: UpdateProfileRequest):
    # TODO: zaktualizuj profil zalogowanego u¿ytkownika
    return
 
 
@router.get("/users/search", response_model=UserSearchResponse)
def search_users(query: str):
    # TODO: wyszukaj u¿ytkowników po username
    return UserSearchResponse(users=[
        UserSearchResult(
            id="00000000-0000-0000-0000-000000000000",
            username="test_user",
        )
    ])