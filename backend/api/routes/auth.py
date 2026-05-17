from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user
from api.schemas.common.base import CreatedIdResponse
from api.schemas.auth.request import (
    RegisterRequest,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
)
from api.schemas.auth.response import CurrentUserResponse
from db.models.user import User


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # TODO: tutaj będzie logika (service + DB)
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.post("/login", response_model=CurrentUserResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # TODO: tutaj będzie logika logowania
    return CurrentUserResponse(
        id="00000000-0000-0000-0000-000000000000",
        username=data.username,
        organization_id=None,
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    # TODO: tu będzie logika sprawdzania sesji
    return CurrentUserResponse(
        id="00000000-0000-0000-0000-000000000000",
        username="test_user",
        organization_id=None,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # TODO: tu będzie logika usunięcia sesji / cookie
    return


@router.post("/request-password-reset", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    # TODO: sprawdzić czy user istnieje (ale NIE ujawniać tego), wygenerować token, wysłać email
    return


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    # TODO: sprawdzić token, zmienić hasło
    return
