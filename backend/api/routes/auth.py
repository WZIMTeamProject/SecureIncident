from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
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
from api.schemas.auth.response import CurrentUserResponse, LoginResponse
from db.models.user import User
from services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

@router.post("/register", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Zarejestruj nowego użytkownika."""
    user = await auth_service.register_user(db, data)
    return CreatedIdResponse(id=user.id)


@router.post("/login", response_model=LoginResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Zaloguj użytkownika i zwróć JWT token."""
    user, token = await auth_service.login_user(db, data)
    return LoginResponse(
        access_token=token,
        user=CurrentUserResponse(
            id=user.id,
            username=user.username,
            organization_id=user.organization_id,
        ),
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    """Pobierz dane aktualnie zalogowanego użytkownika."""
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        organization_id=current_user.organization_id,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Wyloguj użytkownika (stateless — MVP)."""
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.post("/request-password-reset", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Poproś o reset hasła (zawsze 204, nawet jeśli user nie istnieje)."""
    await auth_service.request_password_reset(db, data.email_or_username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """Zresetuj hasło za pomocą tokenu."""
    await auth_service.reset_password(db, data.reset_token, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
