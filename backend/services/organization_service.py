from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.organization.request import (
    CreateOrganizationRequest,
    CreateInviteRequest,
)
from core import security
from db.models.organization import Organization
from db.models.organization_invite import OrganizationInvite
from db.models.user import User
from db import repositories


async def create_organization(
    db: AsyncSession,
    *,
    data: CreateOrganizationRequest,
    current_user: User,
) -> Organization:
    """Utwórz organizację i ustaw twórcę jako właściciela + członka.

    Reguła domenowa: użytkownik może należeć tylko do JEDNEJ organizacji.
    Jeśli już do jakiejś należy, nie może utworzyć kolejnej.
    """
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Użytkownik należy już do organizacji",
        )

    if not data.name or not data.name.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nazwa organizacji jest wymagana",
        )

    organization = await repositories.organization_repo.create_organization(
        db,
        name=data.name.strip(),
        description=data.description,
        owner_id=current_user.id,
    )

    # Twórca staje się członkiem swojej organizacji (ta sama sesja — mutacja jest śledzona).
    current_user.organization_id = organization.id
    db.add(current_user)

    await db.commit()
    await db.refresh(organization)
    return organization


async def get_current_organization(
    db: AsyncSession,
    *,
    current_user: User,
) -> Organization:
    """Zwróć organizację bieżącego użytkownika (404, jeśli nie należy do żadnej)."""
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Użytkownik nie należy do żadnej organizacji",
        )

    organization = await repositories.organization_repo.get_organization_by_id(
        db, current_user.organization_id
    )
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizacja nie znaleziona",
        )
    return organization


async def create_invite(
    db: AsyncSession,
    *,
    data: CreateInviteRequest,
    current_user: User,
) -> tuple[OrganizationInvite, str]:
    """Utwórz zaproszenie do organizacji (tylko właściciel organizacji).

    Zwraca (invite, raw_token). W bazie zapisywany jest TYLKO hasz tokenu —
    surowy token jest jedynie zwracany dzwoniącemu i nie da się go odzyskać później.
    """
    if current_user.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Użytkownik nie należy do żadnej organizacji",
        )

    organization = await repositories.organization_repo.get_organization_by_id(
        db, current_user.organization_id
    )
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizacja nie znaleziona",
        )

    if organization.org_owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tylko właściciel organizacji może tworzyć zaproszenia",
        )

    raw_token = security.generate_token()
    token_hash = security.hash_token(raw_token)

    invite = await repositories.invite_repo.create_organization_invite(
        db,
        organization_id=organization.id,
        created_by_id=current_user.id,
        token_hash=token_hash,
        expires_at=data.expires_at,
        max_uses=data.max_uses,
    )

    return invite, raw_token


async def join_organization(
    db: AsyncSession,
    *,
    current_user: User,
    raw_token: str,
) -> None:
    """Dołącz do organizacji za pomocą tokenu zaproszenia.

    Reguła domenowa: użytkownik może należeć tylko do jednej organizacji —
    jeśli już do jakiejś należy, zwracamy 409 (przed konsumpcją zaproszenia).
    """
    if current_user.organization_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Użytkownik należy już do organizacji",
        )

    token_hash = security.hash_token(raw_token)

    # Atomowe zwiększenie use_count — tylko jeśli zaproszenie jest ważne.
    invite = await repositories.invite_repo.get_and_increment_invite(db, token_hash)
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowe lub wygasłe zaproszenie",
        )

    if invite.scope != "ORGANIZATION" or invite.organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="To zaproszenie nie jest do organizacji",
        )

    current_user.organization_id = invite.organization_id
    db.add(current_user)
    await db.commit()