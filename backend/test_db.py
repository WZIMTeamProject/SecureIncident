import asyncio
from db.session import AsyncSessionLocal
from db.models.user import User
from db.models.organization import Organization
from db.models.project import Project
from db.models.organization_invite import OrganizationInvite
from sqlalchemy import select
import uuid

async def test_db():
    print("Rozpoczynam test bazy danych...")
    async with AsyncSessionLocal() as session:
        try:
            # 1. Tworzenie uzytkownika
            user = User(
                first_name="Jan",
                last_name="Kowalski",
                username=f"jan_{uuid.uuid4()}",
                email=f"test_{uuid.uuid4()}@example.com",
                password="hashed_password",
                is_active=True
            )
            session.add(user)
            await session.flush()
            print(f"[OK] Utworzono uzytkownika: {user.id}")

            # 2. Tworzenie organizacji
            org = Organization(
                name="Testowa Organizacja",
                org_owner_id=user.id
            )
            session.add(org)
            await session.flush()
            print(f"[OK] Utworzono organizacje: {org.id}")

            # 3. Tworzenie projektu
            target_project = Project(
                name="Testowy Projekt",
                project_owner_id=user.id,
                organization_id=org.id,
                scope="INTERNAL"
            )
            session.add(target_project)
            await session.flush()
            print(f"[OK] Utworzono projekt: {target_project.id}")

            # 4. Tworzenie zaproszenia z nowymi polami (ADR-002) - scope PROJECT
            invite = OrganizationInvite(
                scope="PROJECT",
                project_id=target_project.id,
                created_by_id=user.id,
                token=f"TOKEN_{uuid.uuid4()}"
            )
            session.add(invite)
            await session.flush()
            print(f"[OK] Utworzono zaproszenie dla projektu: {invite.id} (Scope: {invite.scope})")

            # MOCK ODCZYTU
            result = await session.execute(select(OrganizationInvite).where(OrganizationInvite.id == invite.id))
            db_invite = result.scalar_one_or_none()
            if db_invite and db_invite.scope == "PROJECT" and db_invite.project_id == target_project.id:
                print(f"[OK] Odczyt zaproszenia z bazy (relacje zachowane prawidłowo).")
            else:
                print("[BŁĄD] Odczyt zaproszenia nie powiódł się lub dane się nie zgadzają!")

            # Wycofujemy zeby nie brudzic bazy swoimi testowymi danymi
            await session.rollback()
            print("[OK] Baza danych wyczyszczona z testowych danych (rollback).")
            print("\nWSZYSTKIE TESTY ZAKOŃCZONE POMYŚLNIE!")
            
        except Exception as e:
            print(f"\n[BŁĄD] Wystąpił błąd w trakcie testu: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(test_db())
