import datetime
import uuid

from core.config import settings
from core.security import decode_token
from db.models.user import User
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Response,
    Security,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials
from services import auth_service
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import bearer_scheme, get_current_user
from api.dependencies.db import get_db
from api.schemas.auth.request import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
)
from api.schemas.auth.response import (
    CurrentUserResponse,
    LoginResponse,
    RefreshResponse,
)
from api.schemas.common.base import CreatedIdResponse, DetailResponse

REFRESH_COOKIE_PATH = "/api/auth/refresh"


def _set_refresh_cookie(response: Response, raw_token: str, max_age: int) -> None:
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        raw_token,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=REFRESH_COOKIE_PATH,
        max_age=max_age,
    )


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    user = await auth_service.register_user(db, data)
    return CreatedIdResponse(id=user.id)


@router.post("/login", response_model=LoginResponse)
async def login_user(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user, set the refresh cookie, and return the access token."""
    result = await auth_service.login_user(db, data)
    _set_refresh_cookie(response, result.raw_refresh_token, result.refresh_max_age)
    return LoginResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
        user=CurrentUserResponse(
            id=result.user.id,
            username=result.user.username,
            organization_id=result.user.organization_id,
        ),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Rotate the refresh cookie and issue a new access token (auth-exempt)."""
    raw_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await auth_service.refresh_tokens(db, raw_token)
    _set_refresh_cookie(response, result.raw_refresh_token, result.refresh_max_age)
    return RefreshResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
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
    response: Response,
    token_credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log out: denylist the access token's JTI and revoke its refresh family."""
    payload = decode_token(token_credentials.credentials)
    exp_timestamp = payload.get("exp")
    expires_at = datetime.datetime.fromtimestamp(
        exp_timestamp, tz=datetime.UTC
    ).replace(tzinfo=None)
    # Guard the parse: a malformed family_id claim must not 500 the logout — mirror
    # the defensive handling in get_current_user and fall back to no family revoke.
    family_raw = payload.get("family_id")
    try:
        family_id = uuid.UUID(family_raw) if family_raw else None
    except ValueError:
        family_id = None

    await auth_service.logout(
        db,
        current_user=current_user,
        family_id=family_id,
        access_jti=payload.get("jti"),
        access_exp=expires_at,
    )

    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/request-password-reset", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(
    data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset (always returns 204, even if user does not exist)."""
    await auth_service.request_password_reset(
        db, data.email_or_username, background_tasks
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": DetailResponse,
            "description": "Invalid or expired password reset token.",
        },
    },
)
async def reset_password(
    data: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using a valid reset token."""
    await auth_service.reset_password(db, data.reset_token, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": DetailResponse,
            "description": "Current password is incorrect, or the new password equals the current one.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": DetailResponse,
            "description": "Not authenticated (missing, invalid, expired or revoked token).",
        },
    },
)
async def change_password(
    data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the password of the currently authenticated user."""
    await auth_service.change_password(
        db,
        current_user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
