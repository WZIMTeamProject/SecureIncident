import logging
from typing import Annotated
from uuid import UUID

from core.security import decode_token
from db import repositories
from db.models.user import User
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_db

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a Bearer JWT.

    Rejects expired, malformed, revoked (blocklisted JTI), or inactive accounts.
    """
    if credentials is None:
        logger.warning("Authentication failed: no credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        logger.warning("Token validation failed: token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        logger.warning("Token validation failed: invalid token signature or format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti: str | None = payload.get("jti")
    if jti and await repositories.revoked_token_repo.is_token_revoked(db, jti):
        logger.warning("Token validation failed: token revoked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Optional family check: tokens predating rotation lack the claim and skip it
    # (backward compatible). family_id ties the token to its rotation lineage so
    # logout / reuse detection can revoke every token in the family at once.
    family_id_str: str | None = payload.get("family_id")
    if family_id_str:
        try:
            family_id = UUID(family_id_str)
        except ValueError:
            family_id = None
        if family_id and await repositories.revoked_family_repo.is_family_revoked(
            db, family_id
        ):
            logger.warning("Token validation failed: family revoked")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user_id_str: str | None = payload.get("sub")
    if not user_id_str:
        logger.warning("Token validation failed: missing sub claim in payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.warning("Token validation failed: sub claim is not a valid UUID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await repositories.user_repo.get_user_by_id(db, user_id)

    if user is None:
        logger.warning(
            "Token validation failed: user not found for user_id=%s", user_id
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("Authentication failed: inactive account user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user
