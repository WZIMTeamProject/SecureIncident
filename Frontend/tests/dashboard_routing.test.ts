import { beforeEach, describe, expect, test, vi } from 'vitest'
import {
  dashboardIncidentsAction,
  dashboardOrganizationAction,
  dashboardProjectsAction,
} from '../src/dashboard/routing.ts'
import Api from '../src/data/Api.ts'
import {
  FORM_ACTION,
  FormActions,
  OrganizationForms,
  ProjectForms,
  UserPermissions,
} from '../src/dashboard/forms.ts'

vi.mock('../src/data/Api.ts', () => ({
  __esModule: true,
  default: {
    projects: {
      projectsPost: vi.fn().mockResolvedValue(null),
    },
    organization: {
      organizationInvitesPost: vi.fn().mockResolvedValue(null),
      organizationPost: vi.fn().mockResolvedValue(null),
      organizationJoinPost: vi.fn().mockResolvedValue(undefined),
    },
    incidents: {
      projectsProjectIdIncidentsPost: vi.fn().mockResolvedValue(null),
    },
    roles: {
      projectsProjectIdRolesPost: vi.fn().mockResolvedValue(null),
    },
  },
}))

const mockedApi = vi.mocked(Api, true)

function createFormRequest(
  values: Record<string, string | string[]>,
  method = 'POST'
): Request {
  const formData = new FormData()

  Object.entries(values).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => formData.append(key, item))
    } else {
      formData.set(key, value)
    }
  })

  return new Request('http://localhost/dashboard', {
    method,
    body: formData,
  })
}

describe('dashboardOrganizationAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_dashboard_organization_returns_false_when_action_missing', async () => {
    const request = createFormRequest({})

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_organization_creates_project_with_valid_data', async () => {
  mockedApi.projects.projectsPost.mockResolvedValue(
    { id: 'project-123' } as Awaited<ReturnType<typeof Api.projects.projectsPost>>
  )

  const request = createFormRequest({
    [FORM_ACTION]: FormActions.NewProject,
    [OrganizationForms.ProjectName]: 'Security project',
    [OrganizationForms.Description]: 'Internal project',
  })

  const result = await dashboardOrganizationAction({ request } as never)

  expect(result).toEqual({ ok: true })
  expect(mockedApi.projects.projectsPost).toHaveBeenCalledWith({
    createProjectRequest: {
      name: 'Security project',
      description: 'Internal project',
      scope: 'ORGANIZATION',
    },
  })
})

  test('test_dashboard_organization_returns_false_when_project_name_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewProject,
      [OrganizationForms.Description]: 'Internal project',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.projects.projectsPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_organization_returns_false_when_project_creation_fails', async () => {
    mockedApi.projects.projectsPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewProject,
      [OrganizationForms.ProjectName]: 'Security project',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_organization_creates_invite_with_positive_max_uses', async () => {
    mockedApi.organization.organizationInvitesPost.mockResolvedValue({
      token: 'invite-token-123',
      inviteUrl: 'http://localhost/invite/invite-token-123',
    })

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.InviteUser,
      [OrganizationForms.InviteCount]: '3',
      [OrganizationForms.DurationHours]: '24',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({
      ok: true,
      token: 'invite-token-123',
      inviteUrl: 'http://localhost/invite/invite-token-123',
    })
  })

  test('test_dashboard_organization_returns_false_when_invite_count_is_zero', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FormActions.InviteUser,
      [OrganizationForms.InviteCount]: '0',
      [OrganizationForms.DurationHours]: '24',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.organization.organizationInvitesPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_organization_creates_organization_with_valid_data', async () => {
    mockedApi.organization.organizationPost.mockResolvedValue(
      { id: 'organization-123' } as Awaited<ReturnType<typeof Api.organization.organizationPost>>
    )

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.CreateOrganization,
      [OrganizationForms.OrganizationName]: 'Secure Org',
      [OrganizationForms.Description]: 'Main organization',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.organization.organizationPost).toHaveBeenCalledWith({
      createOrganizationRequest: {
        name: 'Secure Org',
        description: 'Main organization',
      },
    })
  })

  test('test_dashboard_organization_returns_false_when_organization_name_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FormActions.CreateOrganization,
      [OrganizationForms.Description]: 'Main organization',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.organization.organizationPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_organization_joins_organization_with_valid_token', async () => {
    mockedApi.organization.organizationJoinPost.mockResolvedValue(undefined)

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.JoinOrganization,
      [OrganizationForms.InviteToken]: 'invite-token-123',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: true })
  })

  test('test_dashboard_organization_returns_false_when_join_organization_fails', async () => {
    mockedApi.organization.organizationJoinPost.mockRejectedValue(new Error('Invalid token'))

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.JoinOrganization,
      [OrganizationForms.InviteToken]: 'invalid-token',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_organization_returns_true_when_delete_organization_action_used', async () => {
    const request = createFormRequest(
      {
        [FORM_ACTION]: FormActions.DeleteOrganization,
      },
      'DELETE'
    )

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: true })
  })
})

describe('dashboardProjectsAction', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('test_dashboard_projects_returns_false_when_action_missing', async () => {
    const request = createFormRequest({})

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_projects_creates_incident_with_valid_data', async () => {
    mockedApi.incidents.projectsProjectIdIncidentsPost.mockResolvedValue(
      { id: 'incident-123' } as Awaited<ReturnType<typeof Api.projects.projectsPost>>
    )

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewIncident,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.IncidentName]: 'Login broken',
      [ProjectForms.IncidentDescription]: 'Users cannot log in',
      [ProjectForms.IncidentPriority]: 'HIGH',
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.incidents.projectsProjectIdIncidentsPost).toHaveBeenCalledWith({
      projectId: 'project-123',
      createIncidentRequest: {
        title: 'Login broken',
        description: 'Users cannot log in',
        priority: 'HIGH',
      },
    })
  })

  test('test_dashboard_projects_returns_false_when_incident_description_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewIncident,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.IncidentName]: 'Login broken',
      [ProjectForms.IncidentPriority]: 'HIGH',
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.incidents.projectsProjectIdIncidentsPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_projects_returns_false_when_incident_creation_fails', async () => {
    mockedApi.incidents.projectsProjectIdIncidentsPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewIncident,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.IncidentName]: 'Login broken',
      [ProjectForms.IncidentDescription]: 'Users cannot log in',
      [ProjectForms.IncidentPriority]: 'HIGH',
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_projects_creates_role_with_selected_permissions', async () => {
    mockedApi.roles.projectsProjectIdRolesPost.mockResolvedValue(
      { id: 'role-123' } as Awaited<ReturnType<typeof Api.roles.projectsProjectIdRolesPost>>
    )

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewRole,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.RoleName]: 'Coordinator',
      [ProjectForms.RolePermissions]: [
        UserPermissions.AssignToProject,
        UserPermissions.ChangeStatus,
        UserPermissions.WriteTickets,
      ],
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.roles.projectsProjectIdRolesPost).toHaveBeenCalledWith({
      projectId: 'project-123',
      createRoleRequest: {
        name: 'Coordinator',
        permissions: {
          canAssignHelp: false,
          canChangeRoles: false,
          canMakeRoles: false,
          canHelp: false,
          canAssignPeopleToProject: true,
          canChangeStatus: true,
          canWriteTickets: true,
        },
      },
    })
  })

  test('test_dashboard_projects_creates_role_with_all_permissions', async () => {
    mockedApi.roles.projectsProjectIdRolesPost.mockResolvedValue(
      { id: 'role-123' } as Awaited<ReturnType<typeof Api.roles.projectsProjectIdRolesPost>>
    )

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewRole,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.RoleName]: 'Admin',
      [ProjectForms.RolePermissions]: [
        UserPermissions.AssignHelp,
        UserPermissions.AssignToProject,
        UserPermissions.ChangeRoles,
        UserPermissions.ChangeStatus,
        UserPermissions.Help,
        UserPermissions.MakeRoles,
        UserPermissions.WriteTickets,
      ],
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: true })
    expect(mockedApi.roles.projectsProjectIdRolesPost).toHaveBeenCalledWith({
      projectId: 'project-123',
      createRoleRequest: {
        name: 'Admin',
        permissions: {
          canAssignHelp: true,
          canChangeRoles: true,
          canMakeRoles: true,
          canHelp: true,
          canAssignPeopleToProject: true,
          canChangeStatus: true,
          canWriteTickets: true,
        },
      },
    })
  })

  test('test_dashboard_projects_returns_false_when_role_name_missing', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewRole,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.RolePermissions]: [UserPermissions.WriteTickets],
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.roles.projectsProjectIdRolesPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_projects_returns_false_when_role_creation_fails', async () => {
    mockedApi.roles.projectsProjectIdRolesPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FormActions.NewRole,
      [ProjectForms.ProjectId]: 'project-123',
      [ProjectForms.RoleName]: 'Coordinator',
      [ProjectForms.RolePermissions]: [UserPermissions.WriteTickets],
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })
})

describe('dashboardIncidentsAction', () => {
  test('test_dashboard_incidents_returns_false_when_action_missing', async () => {
    const request = createFormRequest({})

    const result = await dashboardIncidentsAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_incidents_returns_true_when_action_exists', async () => {
    const request = createFormRequest({
      [FORM_ACTION]: 'any_action',
    })

    const result = await dashboardIncidentsAction({ request } as never)

    expect(result).toEqual({ ok: true })
  })
})
