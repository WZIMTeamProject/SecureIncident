import asyncio
import os
import uuid
from pathlib import Path
from sqlalchemy import text
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

from datetime import datetime, timedelta, timezone
from db.models import User, Project, Organization, Role
from db.models.organization_invite import OrganizationInvite
from core.security import create_access_token, generate_token, hash_token
from core.config import settings
from core.security import hash_password

TEST_DATABASE_URL: str = settings.DATABASE_URL
BACKEND_DIR = Path(__file__).parent.parent

@pytest.fixture(scope="session")
def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

    async def setup_schema():
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
            from db.base import Base
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup_schema())

    # Stamp alembic_version so the app's startup migration check sees an up-to-date DB
    # and does not attempt to re-create tables that create_all already built.
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    alembic_cfg = AlembicConfig(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    alembic_command.stamp(alembic_cfg, "head")

    yield engine

    async def teardown_engine():
        await engine.dispose()

    asyncio.run(teardown_engine())

@pytest.fixture(scope="function")
async def db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous database fixture for each test (scope='function').
    Works seamlessly with pytest-asyncio default event loop.
    """
    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        
        async_session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"  # Captures and isolates internal application commits
        )
        
        yield async_session
        
        await async_session.close()
        await transaction.rollback()  # Clean rollback after each test

@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX AsyncClient for testing FastAPI endpoints."""
    from main import app as fastapi_app
    from api.dependencies.db import get_db 
    
    fastapi_app.dependency_overrides[get_db] = lambda: db
    
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac
        
    fastapi_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_org(db: AsyncSession) -> Organization:
    """Creates a test organization, correctly resolving the foreign key ordering problem."""

    # 1. Create a temporary user who will be the owner.
    # Because organization_id is nullable=True, the database will allow saving it.
    owner = User(
        username=f"owner_{uuid.uuid4().hex[:6]}",  # Unique username to avoid 409
        email=f"owner_{uuid.uuid4().hex[:6]}@example.com",
        first_name="Org",
        last_name="Owner",
        password=hash_password("TestPassword123!"),
        is_active=True,
        organization_id=None  # No organization yet
    )
    db.add(owner)
    await db.flush()  # Generate the owner's id in the database

    # 2. Now we can safely create the organization,
    # because we already have a valid, existing owner id (org_owner_id).
    org = Organization(
        name="Test Acme Corp",
        description="Test organization for pytest",
        join_code=f"JOIN_{uuid.uuid4().hex[:6]}",  # Unique join code
        org_owner_id=owner.id  # Assign the user we just created
    )
    db.add(org)
    await db.flush()  # Generate the organization's id

    # 3. Optional but clean step:
    # Now that the organization exists, assign it back to the owner as well.
    owner.organization_id = org.id
    await db.flush()

    # 4. Pass the object to tests and other fixtures
    yield org

@pytest.fixture(scope="function")
async def test_user(db: AsyncSession, test_org: Organization) -> User:
    """Create regular user assigned to organization from test_org fixture."""
    
    user = User(
        username="testuser",
        email="testuser@example.com",
        first_name="Jan",
        last_name="Kowalski",
        password=hash_password("TestPassword123!"),
        is_active=True,
        organization_id=test_org.id  # <--- Here test_org will not be None!
    )
    db.add(user)
    await db.flush()
    
    yield user

@pytest.fixture(scope="function")
async def inactive_user(db: AsyncSession, test_org: Organization) -> User:
    """Fixture creating inactive user for authorization tests."""
    user = User(
        username="inactive_user",
        email="inactive@example.com",
        first_name="Test",
        last_name="Inactive",
        password=hash_password("TestPassword123!"), #
        is_active=False,                               
        organization_id=test_org.id
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    yield user

@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict[str, str]:
    """Generates valid Bearer Authorization headers for the test user."""
    # Ensure this matches the payload format your backend expects
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
async def test_project(db: AsyncSession, test_org: Organization, test_user: User) -> Project:
    """Pre-created Project row."""
    project = Project(
        name="Alpha Project",
        organization_id=test_org.id,
        project_owner_id=test_user.id,
        scope="ORGANIZATION",
    )
    db.add(project)
    await db.flush()
    return project


@pytest.fixture(scope="function")
async def test_role(db: AsyncSession, test_project: Project) -> Role:
    """Pre-created Role row for test_project."""
    role = Role(
        project_id=test_project.id,
        name="Member",
    )
    db.add(role)
    await db.flush()
    return role


@pytest.fixture(scope="function")
async def test_invite(db: AsyncSession, test_project: Project, test_user: User, test_role: Role):
    """Valid project invite fixture. Returns (invite, raw_token)."""
    raw_token = generate_token()
    token_hash = hash_token(raw_token)
    invite = OrganizationInvite(
        scope="PROJECT",
        project_id=test_project.id,
        role_id=test_role.id,
        created_by_id=test_user.id,
        token=token_hash,
        organization_id=None,
    )
    db.add(invite)
    await db.flush()
    return invite, raw_token


@pytest.fixture(scope="function")
async def expired_invite(db: AsyncSession, test_project: Project, test_user: User, test_role: Role):
    """Expired project invite (expires_at in the past). Returns (invite, raw_token)."""
    raw_token = generate_token()
    token_hash = hash_token(raw_token)
    invite = OrganizationInvite(
        scope="PROJECT",
        project_id=test_project.id,
        role_id=test_role.id,
        created_by_id=test_user.id,
        token=token_hash,
        organization_id=None,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
    )
    db.add(invite)
    await db.flush()
    return invite, raw_token


@pytest.fixture(scope="function")
async def exhausted_invite(db: AsyncSession, test_project: Project, test_user: User, test_role: Role):
    """Exhausted project invite (max_uses=1, use_count=1). Returns (invite, raw_token)."""
    raw_token = generate_token()
    token_hash = hash_token(raw_token)
    invite = OrganizationInvite(
        scope="PROJECT",
        project_id=test_project.id,
        role_id=test_role.id,
        created_by_id=test_user.id,
        token=token_hash,
        organization_id=None,
        max_uses=1,
        use_count=1,
    )
    db.add(invite)
    await db.flush()
    return invite, raw_token