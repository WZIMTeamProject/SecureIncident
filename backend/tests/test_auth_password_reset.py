from datetime import UTC, datetime, timedelta

from core import security
from db.models.password_reset_token import PasswordResetToken
from db.models.user import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TestRequestPasswordReset:
    async def test_request_password_reset_returns_204_when_email_exists(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": test_user.email},
        )
        assert response.status_code == 204

    async def test_request_password_reset_returns_204_when_email_does_not_exist(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": "nonexistent@example.com"},
        )
        assert response.status_code == 204

    async def test_request_password_reset_returns_204_when_username_provided(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": test_user.username},
        )
        assert response.status_code == 204

    async def test_request_password_reset_creates_db_token_record(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": test_user.email},
        )
        result = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == test_user.id)
        )
        token_record = result.scalar_one_or_none()
        assert token_record is not None

    async def test_request_password_reset_stores_hashed_not_raw_token(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": test_user.email},
        )
        result = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == test_user.id)
        )
        token_record = result.scalar_one_or_none()
        assert token_record is not None
        assert len(token_record.token) == 64

    async def test_request_password_reset_token_expires_in_30_minutes(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        await client.post(
            "/api/auth/request-password-reset",
            json={"email_or_username": test_user.email},
        )
        result = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == test_user.id)
        )
        token_record = result.scalar_one_or_none()

        assert token_record is not None
        now = datetime.now(UTC).replace(
            tzinfo=None
        )  # naive — matches DB column type (TIMESTAMP WITHOUT TIME ZONE)
        ttl_minutes = (token_record.expires_at - now).total_seconds() / 60
        assert 25 < ttl_minutes < 35


class TestResetPassword:
    async def test_reset_password_returns_204_with_valid_token(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
        )
        db.add(token_record)
        await db.commit()

        response = await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "NewSecurePass123!"},
        )
        assert response.status_code == 204

    async def test_reset_password_updates_user_password_in_db(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        old_password_hash = test_user.password

        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
        )
        db.add(token_record)
        await db.commit()

        await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "NewSecurePass123!"},
        )

        await db.refresh(test_user)
        assert test_user.password != old_password_hash

    async def test_reset_password_marks_token_as_used(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
        )
        db.add(token_record)
        await db.commit()

        await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "NewSecurePass123!"},
        )

        await db.refresh(token_record)
        assert token_record.used_at is not None

    async def test_reset_password_old_credentials_no_longer_work_after_reset(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
        )
        db.add(token_record)
        await db.commit()

        await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "NewSecurePass123!"},
        )

        response = await client.post(
            "/api/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123!",
                "remember_user": False,
            },
        )
        assert response.status_code == 401

    async def test_reset_password_returns_400_with_invalid_token(
        self, client: AsyncClient
    ):
        response = await client.post(
            "/api/auth/reset-password",
            json={"reset_token": "invalid-token", "new_password": "NewSecurePass123!"},
        )
        assert response.status_code == 400

    async def test_reset_password_returns_400_with_expired_token(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
        )
        db.add(token_record)
        await db.commit()

        response = await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "NewSecurePass123!"},
        )
        assert response.status_code == 400

    async def test_reset_password_returns_400_when_token_already_used(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
            used_at=datetime.now(UTC).replace(tzinfo=None),
        )
        db.add(token_record)
        await db.commit()

        response = await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "NewSecurePass123!"},
        )
        assert response.status_code == 400

    async def test_reset_password_returns_422_when_new_password_too_short(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        raw_token = security.generate_token()
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(hours=1)

        token_record = PasswordResetToken(
            user_id=test_user.id,
            token=token_hash,
            expires_at=expires_at,
        )
        db.add(token_record)
        await db.commit()

        response = await client.post(
            "/api/auth/reset-password",
            json={"reset_token": raw_token, "new_password": "Short1!"},
        )
        assert response.status_code == 422
