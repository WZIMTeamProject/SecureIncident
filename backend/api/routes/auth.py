from fastapi import APIRouter, status
from api.schemas.common.base import CreatedIdResponse
from api.schemas.auth.request import (
    RegisterRequest,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from api.schemas.auth.response import CurrentUserResponse



router = APIRouter(prefix="/auth", tags=["Auth"])



@router.post("/register", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterRequest):
    # TODO: tutaj będzie logika (service + DB)
    
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")



@router.post("/login", response_model=CurrentUserResponse)
def login_user(data: LoginRequest):
    # TODO: 
    # tutaj będzie logika logowania
    
    return CurrentUserResponse(
        id="00000000-0000-0000-0000-000000000000",
        username=data.username,
        organizationId=None
    )



@router.get("/me", response_model=CurrentUserResponse)
def get_current_user():
    # TODO: 
    # tu będzie logika sprawdzania sesji
    
    return CurrentUserResponse(
        id="00000000-0000-0000-0000-000000000000",
        username="test_user",
        organizationId=None
    )



@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user():
    # TODO: 
    # tu będzie logika usunięcia sesji / cookie
    
    return



@router.post("/request-password-reset", status_code=status.HTTP_204_NO_CONTENT)
def request_password_reset(data: PasswordResetRequest):
    # TODO:
    # - sprawdzić czy user istnieje (ale NIE ujawniać tego)
    # - wygenerować token
    # - wysłać email
    
    return



@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(data: PasswordResetConfirmRequest):
    # TODO:
    # - sprawdzić token
    # - zmienić hasło
    
    return

