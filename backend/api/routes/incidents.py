from fastapi import APIRouter, status
from uuid import UUID
from typing import Optional
from datetime import datetime
 
from api.schemas.incident.request import (
    CreateIncidentRequest,
    UpdateIncidentStatusRequest,
    UpdateIncidentAssigneeRequest,
    UpdateIncidentPriorityRequest,
    UpdateIncidentCategoryRequest,
    AddCommentRequest,
    AddHelperRequest,
)
from api.schemas.incident.response import (
    IncidentListResponse,
    IncidentDetailsResponse,
    CreatedIdResponse,
    CommentListResponse,
    IncidentLogListResponse,
)
from api.schemas.common.enums import (
    IncidentPriority,
    IncidentStatus
) 
from api.schemas.incident.log import (
    IncidentListResponse,
    IncidentLogEntry,
    IncidentLogType
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
    # TODO: pobierz incydenty zg³oszone przez zalogowanego uzytkownika
    return IncidentListResponse(incidents=[])
 
 
@router.get("/incidents/my-assigned", response_model=IncidentListResponse)
def get_my_assigned():
    # TODO: pobierz incydenty przypisane do zalogowanego uzytkownika
    return IncidentListResponse(incidents=[])

@router.get("/incidents/history", response_model=IncidentLogListResponse)
def get_incident_history(project_id: Optional[UUID] = None, type: Optional[IncidentLogType] = None):
    # TODO: pobierz historiê incydentów u¿ytkownika
    return IncidentLogListResponse(logs=[])


@router.get("/incidents/{incident_id}", response_model=IncidentDetailsResponse)
def get_incident(incident_id: UUID):
    # TODO: pobierz szczego³y incydentu
    return IncidentDetailsResponse(
        id=incident_id,
        projectId="00000000-0000-0000-0000-000000000000",
        title="Test incident",
        description="Test description",
        categoryId="00000000-0000-0000-0000-000000000000",
        priority=IncidentPriority.LOW,
        status=IncidentStatus.OPEN,
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
    # TODO: zaktualizuj przypisan¹ osobe
    return
 
 
@router.patch("/incidents/{incident_id}/priority", status_code=status.HTTP_204_NO_CONTENT)
def update_incident_priority(incident_id: UUID, body: UpdateIncidentPriorityRequest):
    # TODO: zaktualizuj priorytet incydentu
    return
 
 
@router.patch("/incidents/{incident_id}/category", status_code=status.HTTP_204_NO_CONTENT)
def update_incident_category(incident_id: UUID, body: UpdateIncidentCategoryRequest):
    # TODO: zaktualizuj kategorie incydentu
    return

@router.post("/incidents/{incident_id}/close", status_code=status.HTTP_204_NO_CONTENT)
def close_incident(incident_id: UUID):
    # TODO: logika zamkniêcia incydentu (zamiana statusu na CLOSED)
    return

@router.post("/incidents/{incident_id}/request-reassignment", status_code=status.HTTP_204_NO_CONTENT)
def request_reassignment(incident_id: UUID):
    # TODO: logika tworzenia wniosku
    return

@router.post("/incidents/{incident_id}/helpers", status_code=status.HTTP_204_NO_CONTENT)
async def add_helper(incident_id: UUID, body: AddHelperRequest):
    # TODO: logika dodania helpera do do incydentu
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