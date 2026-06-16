from uuid import UUID
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.project.request import (
    CreateProjectRequest,
    UpdateProjectRequest,
    AddProjectMemberRequest,
    AssignRoleRequest,
    ProjectScope,
)
from db.models.project import Project
from db.models.user import User
from db import repositories


# ADR-001: rola właściciela ma wszystkie uprawnienia. Seedowana atomowo z projektem.
_OWNER_PERMISSIONS = {
    "can_write_tickets": True,
    "can_help": True,
    "can_assign_help": True,
    "can_change_status": True,
    "can_make_roles": True,
    "can_change_roles": True,
    "can_assign_people_to_project": True,
}


async def create_project(
    db: AsyncSession,
    *,
    data: CreateProjectRequest,
    current_user: User,
) -> Project:
    """Utwórz projekt z atomowym seedowaniem roli "Owner" i członkostwa właściciela.

    Reguła nadrzędna (architecture.md): użytkownik należy do JEDNEJ organizacji
    ALBO używa tylko projektów prywatnych — nie obu naraz. Z tego wynika:

    - scope=ORGANIZATION  → user MUSI należeć do organizacji; właścicielem projektu
      zostaje właściciel organizacji (ADR-002), nawet jeśli tworzy go delegat.
    - scope=PRIVATE       → user NIE MOŻE należeć do organizacji; właścicielem
      zostaje twórca.

    Wszystko (Project + Role "Owner" + UserProject) powstaje w jednej transakcji.
    """
    if data.scope == ProjectScope.ORGANIZATION:
        if current_user.organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tylko członek organizacji może tworzyć projekty organizacyjne",
            )
        organization = await repositories.organization_repo.get_organization_by_id(
            db, current_user.organization_id
        )
        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organizacja nie znaleziona",
            )
        owner_id = organization.org_owner_id          # ADR-002
        organization_id: Optional[UUID] = organization.id
    else:  # ProjectScope.PRIVATE
        if current_user.organization_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Członek organizacji nie może tworzyć projektów prywatnych",
            )
        owner_id = current_user.id
        organization_id = None

    # --- jedna transakcja: projekt -> rola Owner -> członkostwo właściciela ---
    project = await repositories.project_repo.create_project(
        db,
        name=data.name.strip(),
        description=data.description,
        scope=data.scope.value,
        owner_id=owner_id,
        organization_id=organization_id,
    )

    owner_role = await repositories.project_repo.create_role(
        db,
        project_id=project.id,
        name="Owner",
        permissions=_OWNER_PERMISSIONS,
    )

    await repositories.project_repo.create_user_project(
        db,
        user_id=owner_id,
        project_id=project.id,
        role_id=owner_role.id,
    )

    await db.commit()
    await db.refresh(project)
    return project


async def list_projects(
    db: AsyncSession,
    *,
    current_user: User,
    scope: Optional[ProjectScope] = None,
) -> Sequence[Project]:
    """Lista projektów, których bieżący użytkownik jest członkiem."""
    return await repositories.project_repo.list_projects_for_user(
        db,
        user_id=current_user.id,
        scope=scope.value if scope is not None else None,
    )


async def get_project(
    db: AsyncSession,
    *,
    project_id: UUID,
    current_user: User,
) -> Project:
    """Pobierz projekt — tylko jeśli użytkownik jest jego członkiem."""
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")

    membership = await repositories.project_repo.get_user_project(
        db, current_user.id, project_id
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Brak dostępu do projektu")
    return project


async def update_project(
    db: AsyncSession,
    *,
    project_id: UUID,
    data: UpdateProjectRequest,
    current_user: User,
) -> None:
    """Zaktualizuj metadane projektu (tylko właściciel)."""
    project = await _get_owned_project(db, project_id, current_user)

    if data.name is not None:
        project.name = data.name.strip()
    if data.description is not None:
        project.description = data.description

    db.add(project)
    await db.commit()


async def list_members(
    db: AsyncSession,
    *,
    project_id: UUID,
    current_user: User,
) -> list[dict]:
    """Lista członków projektu (wymaga członkostwa)."""
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")

    membership = await repositories.project_repo.get_user_project(
        db, current_user.id, project_id
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Brak dostępu do projektu")

    rows = await repositories.project_repo.list_members(db, project_id)
    return [
        {
            "user_id": user.id,
            "username": user.username,
            "role_id": role.id,
            "role_name": role.name,
        }
        for user, role in rows
    ]


async def add_member(
    db: AsyncSession,
    *,
    project_id: UUID,
    data: AddProjectMemberRequest,
    current_user: User,
) -> None:
    """Dodaj użytkownika do projektu z konkretną rolą (tylko właściciel)."""
    await _get_owned_project(db, project_id, current_user)

    user = await repositories.user_repo.get_user_by_id(db, data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    role = await repositories.project_repo.get_role_by_id(db, data.role_id)
    if role is None or role.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="Rola nie znaleziona w tym projekcie"
        )

    existing = await repositories.project_repo.get_user_project(
        db, data.user_id, project_id
    )
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="Użytkownik jest już członkiem projektu"
        )

    await repositories.project_repo.create_user_project(
        db,
        user_id=data.user_id,
        project_id=project_id,
        role_id=data.role_id,
    )
    await db.commit()


async def change_member_role(
    db: AsyncSession,
    *,
    project_id: UUID,
    user_id: UUID,
    data: AssignRoleRequest,
    current_user: User,
) -> None:
    """Zmień rolę członka projektu (tylko właściciel)."""
    await _get_owned_project(db, project_id, current_user)

    role = await repositories.project_repo.get_role_by_id(db, data.role_id)
    if role is None or role.project_id != project_id:
        raise HTTPException(
            status_code=404, detail="Rola nie znaleziona w tym projekcie"
        )

    membership = await repositories.project_repo.get_user_project(
        db, user_id, project_id
    )
    if membership is None:
        raise HTTPException(
            status_code=404, detail="Użytkownik nie jest członkiem projektu"
        )

    await repositories.project_repo.update_user_project_role(
        db, membership=membership, role_id=data.role_id
    )
    await db.commit()


async def _get_owned_project(
    db: AsyncSession, project_id: UUID, current_user: User
) -> Project:
    """Helper: pobierz projekt i sprawdź, że bieżący user jest jego właścicielem.

    MVP: autoryzacja przez porównanie owner FK (bez pełnego RBAC).
    """
    project = await repositories.project_repo.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")
    if project.project_owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Tylko właściciel projektu może wykonać tę operację"
        )
    return project
