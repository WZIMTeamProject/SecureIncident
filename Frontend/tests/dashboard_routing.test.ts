import { beforeEach, describe, expect, test, vi } from 'vitest'
import {
  dashboardIncidentsAction,
  dashboardOrganizationAction,
  dashboardProjectsAction,
} from '../src/dashboard/routing.ts'
import Api from '../src/data/Api.ts'
import {
  FORM_ACTION,
  FORM_ACTION_CREATE_ORGANIZATION,
  FORM_ACTION_DELETE_ORGANIZATION,
  FORM_ACTION_INVITE_USER,
  FORM_ACTION_JOIN_ORGANIZATION,
  FORM_ACTION_NEW_INCIDENT,
  FORM_ACTION_NEW_PROJECT,
  FORM_ACTION_NEW_ROLE,
  FORM_INCIDENT_DESCRIPTION,
  FORM_INCIDENT_NAME,
  FORM_INCIDENT_PRIORITY,
  FORM_INVITE_COUNT,
  FORM_INVITE_DURATION_HOURS,
  FORM_INVITE_TOKEN,
  FORM_ORGANIZATION_DESCRIPTION,
  FORM_ORGANIZATION_NAME,
  FORM_PROJECT_DESCRIPTION,
  FORM_PROJECT_ID,
  FORM_PROJECT_NAME,
  FORM_ROLE_NAME,
  FORM_ROLE_PERMISSION,
  PERM_ASSIGN_HELP,
  PERM_ASSIGN_TO_PROJECT,
  PERM_CHANGE_ROLES,
  PERM_CHANGE_STATUS,
  PERM_HELP,
  PERM_MAKE_ROLES,
  PERM_WRITE_TICKETS,
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
    [FORM_ACTION]: FORM_ACTION_NEW_PROJECT,
    [FORM_PROJECT_NAME]: 'Security project',
    [FORM_PROJECT_DESCRIPTION]: 'Internal project',
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
      [FORM_ACTION]: FORM_ACTION_NEW_PROJECT,
      [FORM_PROJECT_DESCRIPTION]: 'Internal project',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.projects.projectsPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_organization_returns_false_when_project_creation_fails', async () => {
    mockedApi.projects.projectsPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_NEW_PROJECT,
      [FORM_PROJECT_NAME]: 'Security project',
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
      [FORM_ACTION]: FORM_ACTION_INVITE_USER,
      [FORM_INVITE_COUNT]: '3',
      [FORM_INVITE_DURATION_HOURS]: '24',
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
      [FORM_ACTION]: FORM_ACTION_INVITE_USER,
      [FORM_INVITE_COUNT]: '0',
      [FORM_INVITE_DURATION_HOURS]: '24',
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
      [FORM_ACTION]: FORM_ACTION_CREATE_ORGANIZATION,
      [FORM_ORGANIZATION_NAME]: 'Secure Org',
      [FORM_ORGANIZATION_DESCRIPTION]: 'Main organization',
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
      [FORM_ACTION]: FORM_ACTION_CREATE_ORGANIZATION,
      [FORM_ORGANIZATION_DESCRIPTION]: 'Main organization',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.organization.organizationPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_organization_joins_organization_with_valid_token', async () => {
    mockedApi.organization.organizationJoinPost.mockResolvedValue(undefined)

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_JOIN_ORGANIZATION,
      [FORM_INVITE_TOKEN]: 'invite-token-123',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: true })
  })

  test('test_dashboard_organization_returns_false_when_join_organization_fails', async () => {
    mockedApi.organization.organizationJoinPost.mockRejectedValue(new Error('Invalid token'))

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_JOIN_ORGANIZATION,
      [FORM_INVITE_TOKEN]: 'invalid-token',
    })

    const result = await dashboardOrganizationAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_organization_returns_true_when_delete_organization_action_used', async () => {
    const request = createFormRequest(
      {
        [FORM_ACTION]: FORM_ACTION_DELETE_ORGANIZATION,
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
      [FORM_ACTION]: FORM_ACTION_NEW_INCIDENT,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_INCIDENT_NAME]: 'Login broken',
      [FORM_INCIDENT_DESCRIPTION]: 'Users cannot log in',
      [FORM_INCIDENT_PRIORITY]: 'HIGH',
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
      [FORM_ACTION]: FORM_ACTION_NEW_INCIDENT,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_INCIDENT_NAME]: 'Login broken',
      [FORM_INCIDENT_PRIORITY]: 'HIGH',
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.incidents.projectsProjectIdIncidentsPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_projects_returns_false_when_incident_creation_fails', async () => {
    mockedApi.incidents.projectsProjectIdIncidentsPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_NEW_INCIDENT,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_INCIDENT_NAME]: 'Login broken',
      [FORM_INCIDENT_DESCRIPTION]: 'Users cannot log in',
      [FORM_INCIDENT_PRIORITY]: 'HIGH',
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
  })

  test('test_dashboard_projects_creates_role_with_selected_permissions', async () => {
    mockedApi.roles.projectsProjectIdRolesPost.mockResolvedValue(
      { id: 'role-123' } as Awaited<ReturnType<typeof Api.roles.projectsProjectIdRolesPost>>
    )

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_NEW_ROLE,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_ROLE_NAME]: 'Coordinator',
      [FORM_ROLE_PERMISSION]: [
        PERM_ASSIGN_TO_PROJECT,
        PERM_CHANGE_STATUS,
        PERM_WRITE_TICKETS,
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
      [FORM_ACTION]: FORM_ACTION_NEW_ROLE,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_ROLE_NAME]: 'Admin',
      [FORM_ROLE_PERMISSION]: [
        PERM_ASSIGN_HELP,
        PERM_ASSIGN_TO_PROJECT,
        PERM_CHANGE_ROLES,
        PERM_CHANGE_STATUS,
        PERM_HELP,
        PERM_MAKE_ROLES,
        PERM_WRITE_TICKETS,
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
      [FORM_ACTION]: FORM_ACTION_NEW_ROLE,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_ROLE_PERMISSION]: [PERM_WRITE_TICKETS],
    })

    const result = await dashboardProjectsAction({ request } as never)

    expect(result).toEqual({ ok: false })
    expect(mockedApi.roles.projectsProjectIdRolesPost).not.toHaveBeenCalled()
  })

  test('test_dashboard_projects_returns_false_when_role_creation_fails', async () => {
    mockedApi.roles.projectsProjectIdRolesPost.mockRejectedValue(new Error('API error'))

    const request = createFormRequest({
      [FORM_ACTION]: FORM_ACTION_NEW_ROLE,
      [FORM_PROJECT_ID]: 'project-123',
      [FORM_ROLE_NAME]: 'Coordinator',
      [FORM_ROLE_PERMISSION]: [PERM_WRITE_TICKETS],
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