import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db
from api.dependencies.auth import get_current_user, bearer_scheme
from api.schemas.common.base import CreatedIdResponse
from api.schemas.auth.request import (
    RegisterRequest,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
)
from api.schemas.auth.response import CurrentUserResponse, LoginResponse
from db.models.user import User
from db import repositories
from services import auth_service
from core.security import decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    user = await auth_service.register_user(db, data)
    return CreatedIdResponse(id=user.id)


@router.post("/login", response_model=LoginResponse)
async def login_user(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
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
    """Retrieve current authenticated user profile."""
    return CurrentUserResponse(
        id=current_user.id,
        username=current_user.username,
        organization_id=current_user.organization_id,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    token_credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log out the user by adding the token's unique JTI to the revocation list."""
    token = token_credentials.credentials
    payload = decode_token(token)
    jti = payload.get("jti")
    exp_timestamp = payload.get("exp")
    expires_at = datetime.datetime.fromtimestamp(exp_timestamp, tz=datetime.timezone.utc).replace(tzinfo=None)

    await repositories.revoked_token_repo.cleanup_expired_revoked_tokens(db)

    await repositories.revoked_token_repo.add_revoked_token(
        db,
        jti=jti,
        user_id=current_user.id,
        expires_at=expires_at
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/request-password-reset", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset (always returns 204, even if user does not exist)."""
    await auth_service.request_password_reset(db, data.email_or_username, background_tasks)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a valid reset token."""
    await auth_service.reset_password(db, data.reset_token, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
