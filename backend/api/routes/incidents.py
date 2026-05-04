from fastapi import APIRouter, status
from uuid import UUID
from typing import Optional
from datetime import datetime
from backend.api.schemas.common.base import CreatedIdResponse
from backend.api.schemas.incident.request import (
    CreateIncidentRequest,
    UpdateIncidentStatusRequest,
    UpdateIncidentAssigneeRequest,
    UpdateIncidentPriorityRequest,
    UpdateIncidentCategoryRequest,
    AddCommentRequest,
    AddHelperRequest,
)
from backend.api.schemas.incident.response import (
    IncidentListResponse,
    IncidentDetailsResponse,
)
from backend.api.schemas.incident.comment import CommentListResponse
from backend.api.schemas.incident.log import IncidentLogListResponse
from backend.api.schemas.common.enums import (
    IncidentPriority,
    IncidentStatus,
    IncidentLogType,
)

router = APIRouter(tags=["Incidents"])


@router.get("/projects/{project_id}/incidents", response_model=IncidentListResponse)
def get_incidents(project_id: UUID):
    # TODO: pobierz incydenty dla projektu
    return IncidentListResponse(incidents=[])


@router.post("/projects/{project_id}/incidents", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def create_incident(project_id: UUID, body: CreateIncidentRequest):
    # TODO: utworz incydent w projekcie
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("/incidents/my-reported", response_model=IncidentListResponse)
def get_my_reported():
    # TODO: pobierz incydenty zgłoszone przez zalogowanego użytkownika
    return IncidentListResponse(incidents=[])


@router.get("/incidents/my-assigned", response_model=IncidentListResponse)
def get_my_assigned():
    # TODO: pobierz incydenty przypisane do zalogowanego użytkownika
    return IncidentListResponse(incidents=[])


@router.get("/incidents/history", response_model=IncidentLogListResponse)
def get_incident_history(project_id: Optional[UUID] = None, type: Optional[IncidentLogType] = None):
    # TODO: pobierz historię incydentów użytkownika
    return IncidentLogListResponse(logs=[])


@router.get("/incidents/{incident_id}", response_model=IncidentDetailsResponse)
def get_incident(incident_id: UUID):
    # TODO: pobierz szczegóły incydentu
    return IncidentDetailsResponse(
        id=incident_id,
        projectId="00000000-0000-0000-0000-000000000000",
        title="Test incident",
        description="Test description",
        categoryId="00000000-0000-0000-0000-000000000000",
        priority=IncidentPriority.LOW,
        status=IncidentStatus.NEW,
        reporterId="00000000-0000-0000-0000-000000000000",
        primaryAssigneeId=None,
        reportDate=datetime.now(),
    )


@router.patch("/incidents/{incident_id}/status", status_code=status.HTTP_204_NO_CONTENT)
def update_incident_status(incident_id: UUID, body: UpdateIncidentStatusRequest):
    # TODO: zaktualizuj status incydentu
    return


@router.patch("/incidents/{incident_id}/assignee", status_code=status.HTTP_204_NO_CONTENT)
def update_incident_assignee(incident_id: UUID, body: UpdateIncidentAssigneeRequest):
    # TODO: zaktualizuj przypisaną osobę
    return


@router.patch("/incidents/{incident_id}/priority", status_code=status.HTTP_204_NO_CONTENT)
def update_incident_priority(incident_id: UUID, body: UpdateIncidentPriorityRequest):
    # TODO: zaktualizuj priorytet incydentu
    return


@router.patch("/incidents/{incident_id}/category", status_code=status.HTTP_204_NO_CONTENT)
def update_incident_category(incident_id: UUID, body: UpdateIncidentCategoryRequest):
    # TODO: zaktualizuj kategorię incydentu
    return


@router.post("/incidents/{incident_id}/close", status_code=status.HTTP_204_NO_CONTENT)
def close_incident(incident_id: UUID):
    # TODO: logika zamknięcia incydentu (zmiana statusu na CLOSED)
    return


@router.post("/incidents/{incident_id}/request-reassignment", status_code=status.HTTP_204_NO_CONTENT)
def request_reassignment(incident_id: UUID):
    # TODO: logika tworzenia wniosku o zmianę przypisania
    return


@router.post("/incidents/{incident_id}/helpers", status_code=status.HTTP_204_NO_CONTENT)
def add_helper(incident_id: UUID, body: AddHelperRequest):
    # TODO: logika dodania helpera do incydentu
    return


@router.delete("/incidents/{incident_id}/helpers/{helper_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_helper(incident_id: UUID, helper_id: UUID):
    # TODO: logika usunięcia helpera z incydentu
    return


@router.get("/incidents/{incident_id}/comments", response_model=CommentListResponse)
def get_comments(incident_id: UUID):
    # TODO: pobierz komentarze incydentu
    return CommentListResponse(comments=[])


@router.post("/incidents/{incident_id}/comments", response_model=CreatedIdResponse, status_code=status.HTTP_201_CREATED)
def add_comment(incident_id: UUID, body: AddCommentRequest):
    # TODO: dodaj komentarz do incydentu
    return CreatedIdResponse(id="00000000-0000-0000-0000-000000000000")


@router.get("/incidents/{incident_id}/logs", response_model=IncidentLogListResponse)
def get_logs(incident_id: UUID):
    # TODO: pobierz logi incydentu
    return IncidentLogListResponse(logs=[])
