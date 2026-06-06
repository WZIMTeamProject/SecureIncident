from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    verify_password,
    create_access_token,
    generate_secure_token,
)
from db.repositories.user_repo import UserRepository


class AuthService:
    """Business authentication service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str,
        password: str,
    ):
        """Register a user."""
        if await self.user_repo.user_exists(username, email):
            raise ValueError("User already exists")
        
        return await self.user_repo.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
    ):
        """Authenticate a user using username and password."""
        user = await self.user_repo.get_user_by_username(username)
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not verify_password(password, user.password):
            return None
        
        return user
    
    async def create_access_token_for_user(
        self,
        user_id: UUID,
        remember_user: bool = False,
    ) -> str:
        """Create an access token for a user."""
        return create_access_token(str(user_id), remember_user=remember_user)
    
    async def request_password_reset(self, email_or_username: str) -> Optional[tuple[str, UUID]]:
        """Get a user's password reset token."""
        user = await self.user_repo.get_user_by_email_or_username(email_or_username)
        if not user:
            return None
        
        raw_token = generate_secure_token()
        await self.user_repo.create_password_reset_token(user.id, raw_token)
        
        return (raw_token, user.id)
    
    async def reset_password(
        self,
        reset_token: str,
        new_password: str,
    ) -> bool:
        """Reset a user's password."""
        result = await self.user_repo.get_valid_password_reset_token(reset_token)
        if not result:
            return False
        
        token_record, user = result
        
        # Marks token as used
        await self.user_repo.mark_token_as_used(token_record)
        
        # Update users password
        await self.user_repo.update_password(user, new_password)
        
        return True