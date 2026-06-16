import asyncio
import os
import uuid
from pathlib import Path
from sqlalchemy import text
from typing import AsyncGenerator, Generator
import pytest
from fastapi import FastAPI, security
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
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
    Asynchroniczny fixture bazy danych dla każdego testu (scope='function').
    Idealnie współpracuje z domyślną pętlą pytest-asyncio.
    """
    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        
        async_session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"  # Przechwytuje i izoluje wewnętrzne commity aplikacji
        )
        
        yield async_session
        
        await async_session.close()
        await transaction.rollback()  # Czysty rollback po każdym teście

@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Klient HTTPX AsyncClient do testowania endpointów FastAPI."""
    from main import app as fastapi_app
    from api.dependencies.db import get_db 
    
    fastapi_app.dependency_overrides[get_db] = lambda: db
    
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac
        
    fastapi_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_org(db: AsyncSession) -> Organization:
    """Tworzy testową organizację, poprawnie rozwiązując problem kluczy obcych."""
    
    # 1. Tworzymy tymczasowego użytkownika, który będzie właścicielem.
    # Ponieważ organization_id jest nullable=True, baza pozwoli go zapisać.
    owner = User(
        username=f"owner_{uuid.uuid4().hex[:6]}",  # Unikalny username, by uniknąć 409
        email=f"owner_{uuid.uuid4().hex[:6]}@example.com",
        first_name="Org",
        last_name="Owner",
        password=hash_password("TestPassword123!"),
        is_active=True,
        organization_id=None  # Na razie bez organizacji
    )
    db.add(owner)
    await db.flush()  # Generujemy id dla ownera w bazie danych

    # 2. Teraz możemy bezpiecznie stworzyć organizację,
    # bo mamy już poprawne, istniejące id właściciela (org_owner_id).
    org = Organization(
        name="Test Acme Corp",
        description="Testowa organizacja na potrzeby pytest",
        join_code=f"JOIN_{uuid.uuid4().hex[:6]}",  # Unikalny kod dołączenia
        org_owner_id=owner.id  # Przypisujemy stworzonego przed chwilą użytkownika
    )
    db.add(org)
    await db.flush()  # Generujemy id dla organizacji

    # 3. Krok opcjonalny, ale elegancki: 
    # Skoro organizacja już istnieje, przypisujemy ją też samemu właścicielowi.
    owner.organization_id = org.id
    await db.flush()

    # 4. PRZEKAZUJEMY obiekt dalej do testów i innych fixture'ów
    yield org

@pytest.fixture(scope="function")
async def test_user(db: AsyncSession, test_org: Organization) -> User:
    """Tworzy zwykłego użytkownika przypisanego do organizacji z fixture'a test_org."""
    
    user = User(
        username="testuser",
        email="testuser@example.com",
        first_name="Jan",
        last_name="Kowalski",
        password=hash_password("TestPassword123!"),
        is_active=True,
        organization_id=test_org.id  # <--- Tutaj test_org nie będzie już None!
    )
    db.add(user)
    await db.flush()
    
    yield user

@pytest.fixture(scope="function")
async def inactive_user(db: AsyncSession, test_org: Organization) -> User:
    """Fixture tworzący nieaktywnego użytkownika dla testów autoryzacji."""
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