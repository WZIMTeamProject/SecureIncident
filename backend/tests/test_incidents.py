import uuid
from uuid import uuid4
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.project import Project
from db.models.incident import Incident
from db.models.role import Role
from db.models.user import User
from db.models.user_project import UserProject


class TestSchemaFixes:
    def test_update_category_request_rejects_null_category_id(self):
        from api.schemas.incident.request import UpdateIncidentCategoryRequest
        with pytest.raises(ValidationError):
            UpdateIncidentCategoryRequest(category_id=None)

    def test_incident_detail_response_includes_closing_date_field(self):
        from api.schemas.incident.response import IncidentDetailsResponse
        from api.schemas.common.enums import IncidentPriority, IncidentStatus
        incident = IncidentDetailsResponse(
            id=uuid4(),
            project_id=uuid4(),
            title="Test",
            description="Test description",
            priority=IncidentPriority.LOW,
            status=IncidentStatus.NEW,
            reporter_id=uuid4(),
            report_date=datetime.now(timezone.utc),
        )
        assert "closing_date" in IncidentDetailsResponse.model_fields
        assert incident.closing_date is None

    def test_incident_detail_response_includes_helpers_list(self):
        from api.schemas.incident.response import IncidentDetailsResponse
        from api.schemas.common.enums import IncidentPriority, IncidentStatus
        incident = IncidentDetailsResponse(
            id=uuid4(),
            project_id=uuid4(),
            title="Test",
            description="Test description",
            priority=IncidentPriority.LOW,
            status=IncidentStatus.NEW,
            reporter_id=uuid4(),
            report_date=datetime.now(timezone.utc),
        )
        assert "helpers" in IncidentDetailsResponse.model_fields
        assert isinstance(incident.helpers, list)


class TestIncidentHelperModel:
    async def test_incident_helper_model_has_composite_pk(self, db: AsyncSession, test_project: Project, test_user: User):
        from db.models.incident_helper import IncidentHelper
        from sqlalchemy import inspect

        incident = Incident(
            project_id=test_project.id,
            reporter_id=test_user.id,
            title="Test Incident",
            description="Test description",
        )
        db.add(incident)
        await db.flush()

        helper = IncidentHelper(incident_id=incident.id, user_id=test_user.id)
        db.add(helper)
        await db.flush()

        mapper = inspect(IncidentHelper)
        pk_columns = [col.key for col in mapper.mapper.primary_key]
        assert "incident_id" in pk_columns
        assert "user_id" in pk_columns

    async def test_incident_helper_added_at_has_server_default(self, db: AsyncSession, test_project: Project, test_user: User):
        from db.models.incident_helper import IncidentHelper
        from sqlalchemy import inspect

        incident = Incident(
            project_id=test_project.id,
            reporter_id=test_user.id,
            title="Test Incident SD",
            description="Test description",
        )
        db.add(incident)
        await db.flush()

        helper = IncidentHelper(incident_id=incident.id, user_id=test_user.id)
        db.add(helper)
        await db.flush()
        await db.refresh(helper)

        assert helper.added_at is not None

    async def test_incident_helper_cascade_delete_from_incident(self, db: AsyncSession, test_project: Project, test_user: User):
        from db.models.incident_helper import IncidentHelper
        from sqlalchemy import select

        incident = Incident(
            project_id=test_project.id,
            reporter_id=test_user.id,
            title="Cascade Test Incident",
            description="Test description",
        )
        db.add(incident)
        await db.flush()

        incident_id = incident.id
        helper = IncidentHelper(incident_id=incident_id, user_id=test_user.id)
        db.add(helper)
        await db.flush()

        await db.delete(incident)
        await db.flush()

        result = await db.execute(
            select(IncidentHelper).where(IncidentHelper.incident_id == incident_id)
        )
        remaining = result.scalars().all()
        assert remaining == []

    async def test_incident_helper_back_populates_on_incident(self, db: AsyncSession, test_project: Project, test_user: User):
        from db.models.incident_helper import IncidentHelper

        incident = Incident(
            project_id=test_project.id,
            reporter_id=test_user.id,
            title="Back-pop Test Incident",
            description="Test description",
        )
        db.add(incident)
        await db.flush()

        helper = IncidentHelper(incident_id=incident.id, user_id=test_user.id)
        db.add(helper)
        await db.flush()
        await db.refresh(incident)

        assert isinstance(incident.helpers, list)
        assert any(h.user_id == test_user.id for h in incident.helpers)


class TestIncidentValidation:
    async def test_create_incident_returns_422_when_title_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "", "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_title_exceeds_200_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "a" * 201, "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_title_is_whitespace_only(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "   ", "description": "valid description"},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_description_is_empty(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "valid title", "description": ""},
        )
        assert response.status_code == 422

    async def test_create_incident_returns_422_when_description_exceeds_2000_chars(
        self, client: AsyncClient, test_project: Project, auth_headers: dict
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
            json={"title": "valid title", "description": "a" * 2001},
        )
        assert response.status_code == 422


class TestServiceLayer:
    async def test_create_incident_service_raises_403_when_not_member(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from services import incident_service
        from api.schemas.incident.request import CreateIncidentRequest

        data = CreateIncidentRequest(title="Test Incident", description="Test description")
        with pytest.raises(HTTPException) as exc_info:
            await incident_service.create_incident(db, test_project.id, data, test_user)
        assert exc_info.value.status_code == 403

    async def test_create_incident_service_raises_403_when_no_write_tickets_permission(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from services import incident_service
        from api.schemas.incident.request import CreateIncidentRequest

        role = Role(project_id=test_project.id, name="ReadOnly", can_write_tickets=False)
        db.add(role)
        await db.flush()
        membership = UserProject(user_id=test_user.id, project_id=test_project.id, role_id=role.id)
        db.add(membership)
        await db.flush()

        data = CreateIncidentRequest(title="Test Incident", description="Test description")
        with pytest.raises(HTTPException) as exc_info:
            await incident_service.create_incident(db, test_project.id, data, test_user)
        assert exc_info.value.status_code == 403

    async def test_create_incident_service_returns_created_id_response(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from services import incident_service
        from api.schemas.incident.request import CreateIncidentRequest
        from api.schemas.common.base import CreatedIdResponse

        role = Role(
            project_id=test_project.id,
            name="FullAccess",
            can_write_tickets=True,
            can_help=True,
            can_assign_help=True,
            can_change_status=True,
            can_make_roles=True,
            can_change_roles=True,
            can_assign_people_to_project=True,
        )
        db.add(role)
        await db.flush()
        membership = UserProject(user_id=test_user.id, project_id=test_project.id, role_id=role.id)
        db.add(membership)
        await db.flush()

        data = CreateIncidentRequest(title="Test Incident", description="Test description")
        result = await incident_service.create_incident(db, test_project.id, data, test_user)
        assert isinstance(result, CreatedIdResponse)
        assert result.id is not None

    async def test_list_categories_service_raises_403_when_not_member(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from services import category_service

        with pytest.raises(HTTPException) as exc_info:
            await category_service.list_categories(db, test_project.id, test_user)
        assert exc_info.value.status_code == 403

    async def test_create_category_service_raises_403_when_no_make_roles(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from services import category_service
        from api.schemas.category.request import CreateCategoryRequest

        role = Role(project_id=test_project.id, name="NoMakeRoles", can_make_roles=False)
        db.add(role)
        await db.flush()
        membership = UserProject(user_id=test_user.id, project_id=test_project.id, role_id=role.id)
        db.add(membership)
        await db.flush()

        data = CreateCategoryRequest(name="Bug", description="Software defects")
        with pytest.raises(HTTPException) as exc_info:
            await category_service.create_category(db, test_project.id, data, test_user)
        assert exc_info.value.status_code == 403


class TestRouteWiring:
    async def test_routes_create_incident_calls_service(
        self, client: AsyncClient, db: AsyncSession, test_project: Project, test_user: User, auth_headers: dict
    ):
        role = Role(
            project_id=test_project.id,
            name="Admin",
            can_write_tickets=True,
            can_help=True,
            can_assign_help=True,
            can_change_status=True,
            can_make_roles=True,
        )
        db.add(role)
        await db.flush()
        from db.models.user_project import UserProject
        membership = UserProject(user_id=test_user.id, project_id=test_project.id, role_id=role.id)
        db.add(membership)
        await db.flush()

        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Test Bug", "description": "Something broke"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert "id" in response.json()

    async def test_routes_get_incident_returns_real_data(
        self, client: AsyncClient, db: AsyncSession, test_project: Project, test_user: User, auth_headers: dict
    ):
        role = Role(
            project_id=test_project.id,
            name="Admin",
            can_write_tickets=True,
            can_help=True,
            can_assign_help=True,
            can_change_status=True,
            can_make_roles=True,
        )
        db.add(role)
        await db.flush()
        from db.models.user_project import UserProject
        membership = UserProject(user_id=test_user.id, project_id=test_project.id, role_id=role.id)
        db.add(membership)
        await db.flush()

        create_resp = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Real Data Incident", "description": "Verify GET wiring"},
            headers=auth_headers,
        )
        assert create_resp.status_code == 201
        incident_id = create_resp.json()["id"]

        get_resp = await client.get(
            f"/api/incidents/{incident_id}",
            headers=auth_headers,
        )
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "Real Data Incident"

    async def test_routes_list_categories_returns_empty_for_new_project(
        self, client: AsyncClient, db: AsyncSession, test_project: Project, test_user: User, auth_headers: dict
    ):
        role = Role(
            project_id=test_project.id,
            name="Admin",
            can_write_tickets=True,
            can_help=True,
            can_assign_help=True,
            can_change_status=True,
            can_make_roles=True,
        )
        db.add(role)
        await db.flush()
        from db.models.user_project import UserProject
        membership = UserProject(user_id=test_user.id, project_id=test_project.id, role_id=role.id)
        db.add(membership)
        await db.flush()

        response = await client.get(
            f"/api/projects/{test_project.id}/categories",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


class TestFixtures:
    async def test_test_membership_fixture_creates_user_project_row(
        self, db: AsyncSession, test_project: Project, test_user: User, test_membership
    ):
        from db import repositories
        membership = await repositories.project_repo.get_user_project(db, test_user.id, test_project.id)
        assert membership is not None
        assert membership.user_id == test_user.id

    async def test_limited_headers_fixture_is_blocked_by_permission_check(
        self, client: AsyncClient, test_project: Project, limited_headers: dict, limited_membership
    ):
        response = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Test", "description": "Test description"},
            headers=limited_headers,
        )
        assert response.status_code == 403


class TestIncidentRepo:
    async def test_incident_repo_get_by_id_returns_none_for_unknown_id(
        self, db: AsyncSession
    ):
        from db.repositories import incident_repo

        result = await incident_repo.get_by_id(db, uuid4())
        assert result is None

    async def test_incident_repo_create_and_get_by_id(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from db.repositories import incident_repo

        incident = Incident(
            reporter_id=test_user.id,
            project_id=test_project.id,
            title="Test",
            description="Desc",
            status="NEW",
            priority="LOW",
        )
        await incident_repo.create(db, incident)
        fetched = await incident_repo.get_by_id(db, incident.id)
        assert fetched is not None
        assert fetched.title == "Test"

    async def test_incident_repo_get_incidents_by_project_returns_paginated(
        self, db: AsyncSession, test_project: Project, test_user: User
    ):
        from db.repositories import incident_repo

        for i in range(2):
            inc = Incident(
                reporter_id=test_user.id,
                project_id=test_project.id,
                title=f"Incident {i}",
                description="Desc",
                status="NEW",
                priority="LOW",
            )
            db.add(inc)
        await db.flush()

        incidents, total = await incident_repo.get_incidents_by_project(
            db, test_project.id, limit=1, offset=0
        )
        assert len(incidents) == 1
        assert total == 2

    async def test_category_repo_create_and_list(
        self, db: AsyncSession, test_project: Project
    ):
        from db.repositories import category_repo
        from db.models.category import Category

        category = Category(
            project_id=test_project.id,
            name="Bug",
            description="Software defects",
        )
        await category_repo.create(db, category)

        categories = await category_repo.get_by_project(db, test_project.id)
        assert any(c.name == "Bug" for c in categories)


class TestCreateIncident:
    async def test_create_incident_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_project
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Bug", "description": "details"},
        )
        assert r.status_code == 401

    async def test_create_incident_returns_403_when_not_project_member(
        self, client: AsyncClient, test_project, non_member_headers
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Bug", "description": "details"},
            headers=non_member_headers,
        )
        assert r.status_code == 403

    async def test_create_incident_returns_403_when_no_can_write_tickets(
        self, client: AsyncClient, test_project, limited_headers, limited_membership
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Bug", "description": "details"},
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_create_incident_returns_201_with_valid_data(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "New Bug", "description": "Something is wrong"},
            headers=auth_headers,
        )
        assert r.status_code == 201
        assert "id" in r.json()

    async def test_create_incident_defaults_priority_to_low(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Priority Test", "description": "check priority"},
            headers=auth_headers,
        )
        assert r.status_code == 201
        incident_id = r.json()["id"]
        detail = await client.get(f"/api/incidents/{incident_id}", headers=auth_headers)
        assert detail.json()["priority"] == "LOW"

    async def test_create_incident_returns_404_for_invalid_category_id(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        fake_cat_id = str(uuid4())
        r = await client.post(
            f"/api/projects/{test_project.id}/incidents",
            json={"title": "Cat Test", "description": "details", "category_id": fake_cat_id},
            headers=auth_headers,
        )
        assert r.status_code == 404


class TestListIncidents:
    async def test_list_incidents_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_project
    ):
        r = await client.get(f"/api/projects/{test_project.id}/incidents")
        assert r.status_code == 401

    async def test_list_incidents_returns_403_when_not_project_member(
        self, client: AsyncClient, test_project, non_member_headers
    ):
        r = await client.get(
            f"/api/projects/{test_project.id}/incidents",
            headers=non_member_headers,
        )
        assert r.status_code == 403

    async def test_list_incidents_returns_200_with_empty_list(
        self, client: AsyncClient, test_project, auth_headers, test_membership
    ):
        r = await client.get(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_incidents_returns_incidents_for_project(
        self, client: AsyncClient, test_project, auth_headers, test_membership, test_incident
    ):
        r = await client.get(
            f"/api/projects/{test_project.id}/incidents",
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Test Incident"


class TestGetIncidentDetail:
    async def test_get_incident_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_incident
    ):
        r = await client.get(f"/api/incidents/{test_incident.id}")
        assert r.status_code == 401

    async def test_get_incident_returns_403_when_not_member(
        self, client: AsyncClient, test_incident, test_membership, non_member_headers
    ):
        r = await client.get(
            f"/api/incidents/{test_incident.id}",
            headers=non_member_headers,
        )
        assert r.status_code == 403

    async def test_get_incident_returns_404_for_nonexistent_id(
        self, client: AsyncClient, auth_headers, test_membership
    ):
        r = await client.get(f"/api/incidents/{uuid4()}", headers=auth_headers)
        assert r.status_code == 404

    async def test_get_incident_returns_200_with_correct_fields(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        r = await client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(test_incident.id)
        assert data["title"] == "Test Incident"
        assert data["helpers"] == []
        assert "report_date" in data


class TestUpdateStatus:
    async def test_update_status_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_incident, test_membership
    ):
        r = await client.patch(
            f"/api/incidents/{test_incident.id}/status",
            json={"status": "PROBLEM_IS_BEING_SOLVED"},
        )
        assert r.status_code == 401

    async def test_update_status_returns_403_when_no_permission(
        self, client: AsyncClient, test_incident, test_membership, limited_headers, limited_membership
    ):
        r = await client.patch(
            f"/api/incidents/{test_incident.id}/status",
            json={"status": "PROBLEM_IS_BEING_SOLVED"},
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_update_status_returns_404_for_nonexistent(
        self, client: AsyncClient, auth_headers, test_membership
    ):
        r = await client.patch(
            f"/api/incidents/{uuid4()}/status",
            json={"status": "PROBLEM_IS_BEING_SOLVED"},
            headers=auth_headers,
        )
        assert r.status_code == 404

    async def test_update_status_returns_204_and_persists_change(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        r = await client.patch(
            f"/api/incidents/{test_incident.id}/status",
            json={"status": "RESOLVED"},
            headers=auth_headers,
        )
        assert r.status_code == 204
        detail = await client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        assert detail.json()["status"] == "RESOLVED"


class TestCloseIncident:
    async def test_close_incident_returns_401_when_not_authenticated(
        self, client: AsyncClient, test_incident, test_membership
    ):
        r = await client.post(f"/api/incidents/{test_incident.id}/close")
        assert r.status_code == 401

    async def test_close_incident_returns_404_for_nonexistent(
        self, client: AsyncClient, auth_headers, test_membership
    ):
        r = await client.post(f"/api/incidents/{uuid4()}/close", headers=auth_headers)
        assert r.status_code == 404

    async def test_close_incident_returns_403_when_no_permission(
        self, client: AsyncClient, test_incident, test_membership, limited_headers, limited_membership
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/close",
            headers=limited_headers,
        )
        assert r.status_code == 403

    async def test_close_incident_returns_204_and_sets_closing_date(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        r = await client.post(
            f"/api/incidents/{test_incident.id}/close",
            headers=auth_headers,
        )
        assert r.status_code == 204
        detail = await client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        data = detail.json()
        assert data["status"] == "CLOSED"
        assert data["closing_date"] is not None

    async def test_close_incident_returns_409_when_already_closed(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        await client.post(f"/api/incidents/{test_incident.id}/close", headers=auth_headers)
        r = await client.post(f"/api/incidents/{test_incident.id}/close", headers=auth_headers)
        assert r.status_code == 409


class TestUpdatePriority:
    async def test_update_priority_returns_204_and_persists(
        self, client: AsyncClient, test_incident, auth_headers, test_membership
    ):
        r = await client.patch(
            f"/api/incidents/{test_incident.id}/priority",
            json={"priority": "HIGH"},
            headers=auth_headers,
        )
        assert r.status_code == 204
        detail = await client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        assert detail.json()["priority"] == "HIGH"


class TestUpdateAssignee:
    async def test_update_assignee_returns_204_and_persists(
        self, client: AsyncClient, test_incident, auth_headers, test_membership, test_user
    ):
        r = await client.patch(
            f"/api/incidents/{test_incident.id}/assignee",
            json={"primary_assignee_id": str(test_user.id)},
            headers=auth_headers,
        )
        assert r.status_code == 204
        detail = await client.get(f"/api/incidents/{test_incident.id}", headers=auth_headers)
        assert detail.json()["primary_assignee_id"] == str(test_user.id)


class TestUpdateCategory:
    async def test_update_category_with_cross_project_category_returns_404(
        self, client: AsyncClient, db, test_incident, auth_headers, test_membership, test_org, test_user
    ):
        from db.models.project import Project
        from db.models.category import Category
        from db.models.role import Role
        from db.models.user_project import UserProject

        other_project = Project(
            name="Other Project",
            organization_id=test_org.id,
            project_owner_id=test_user.id,
            scope="ORGANIZATION",
        )
        db.add(other_project)
        await db.flush()

        other_role = Role(project_id=other_project.id, name="Admin", can_write_tickets=True, can_help=True)
        db.add(other_role)
        await db.flush()

        other_membership = UserProject(user_id=test_user.id, project_id=other_project.id, role_id=other_role.id)
        db.add(other_membership)
        await db.flush()

        other_category = Category(
            project_id=other_project.id,
            name="WrongProject",
            description="A category in a different project",
        )
        db.add(other_category)
        await db.flush()

        r = await client.patch(
            f"/api/incidents/{test_incident.id}/category",
            json={"category_id": str(other_category.id)},
            headers=auth_headers,
        )
        assert r.status_code == 404
