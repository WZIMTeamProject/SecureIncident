from fastapi import HTTPException, status

from db.models.user import User


async def get_current_user() -> User:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
