import {type ActionFunction} from "react-router";
import {
    FORM_ACTION, FORM_ACTION_CREATE_ORGANIZATION,
    FORM_ACTION_DELETE_ORGANIZATION,
    FORM_ACTION_INVITE_USER, FORM_ACTION_JOIN_ORGANIZATION, FORM_ACTION_NEW_INCIDENT,
    FORM_ACTION_NEW_PROJECT, FORM_ACTION_NEW_ROLE,
    FORM_INCIDENT_DESCRIPTION, FORM_INCIDENT_NAME,
    FORM_INCIDENT_PRIORITY, FORM_INVITE_COUNT, FORM_INVITE_DURATION_HOURS, FORM_INVITE_TOKEN, FORM_ORGANIZATION_DESCRIPTION, FORM_ORGANIZATION_NAME,
    FORM_PROJECT_DESCRIPTION, FORM_PROJECT_ID,
    FORM_PROJECT_NAME, FORM_ROLE_NAME, FORM_ROLE_PERMISSION, PERM_ASSIGN_HELP, PERM_ASSIGN_TO_PROJECT,
    PERM_CHANGE_ROLES, PERM_CHANGE_STATUS, PERM_HELP, PERM_MAKE_ROLES, PERM_WRITE_TICKETS
} from "./forms.ts";
import Api from "../data/Api.ts";
import type {IncidentPriority} from "../api";

export const dashboardOrganizationAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    const organizationAction = formData.get(FORM_ACTION)?.toString();
    if (!organizationAction) {
        return {ok: false};
    }

    if (request.method === "POST") {
        if (organizationAction === FORM_ACTION_NEW_PROJECT) {
            const projectName = formData.get(FORM_PROJECT_NAME)?.toString()?.trim();
            const projectDescription = formData.get(FORM_PROJECT_DESCRIPTION)?.toString()?.trim();

            if (projectName) {
                const createdId = await Api.projects.projectsPost({
                    createProjectRequest: {
                        name: projectName,
                        description: projectDescription,
                        scope: "ORGANIZATION"
                    }
                }).catch(() => null);

                if (createdId) {
                    return {ok: true};
                }
            }
        } else if (organizationAction === FORM_ACTION_INVITE_USER) {
            const maxUses = Number(formData.get(FORM_INVITE_COUNT));
            const durationHours = Number(formData.get(FORM_INVITE_DURATION_HOURS));

            if (maxUses > 0) {
                const expiresAt = durationHours > 0
                    ? new Date(Date.now() + durationHours * 3600_000)
                    : undefined;

                const inviteResponse = await Api.organization.organizationInvitesPost({
                    createOrgInviteRequest: {
                        expiresAt: expiresAt,
                        maxUses: maxUses,
                    }
                }).catch(() => null);

                if(inviteResponse) {
                    return {
                        ok: true,
                        token: inviteResponse.token,
                        inviteUrl: inviteResponse.inviteUrl,
                    };
                }
            }
        } else if (organizationAction === FORM_ACTION_CREATE_ORGANIZATION) {
            const organizationName = formData.get(FORM_ORGANIZATION_NAME)?.toString()?.trim();
            const organizationDescription = formData.get(FORM_ORGANIZATION_DESCRIPTION)?.toString()?.trim();

            if (organizationName) {
                const organizationId = await Api.organization.organizationPost({
                    createOrganizationRequest: {
                        name: organizationName,
                        description: organizationDescription,
                    }
                }).catch(() => null);

                if (organizationId) {
                    return {ok: true};
                }
            }
        } else if (organizationAction === FORM_ACTION_JOIN_ORGANIZATION) {
            const token = formData.get(FORM_INVITE_TOKEN)?.toString()?.trim();

            if (token) {
                const joinedSuccessfully = await Api.organization.organizationJoinPost({
                    joinByInviteRequest: {
                        token: token
                    }
                }).then(
                    () => true,
                    () => false
                )

                if (joinedSuccessfully) {
                    return {ok: true};
                }
            }
        }
    } else if (request.method === "DELETE") {
        if (organizationAction === FORM_ACTION_DELETE_ORGANIZATION) {
            // TODO
            return {ok: true}
        }
    }

    return {ok: false};
};

export const dashboardProjectsAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    const projectAction = formData.get(FORM_ACTION)?.toString();
    if (!projectAction) {
        return {ok: false};
    }

    const projectId = formData.get(FORM_PROJECT_ID)?.toString()?.trim();

    if (request.method === "POST") {
        if (projectAction === FORM_ACTION_NEW_INCIDENT) {
            const incidentName = formData.get(FORM_INCIDENT_NAME)?.toString()?.trim();
            const incidentDescription = formData.get(FORM_INCIDENT_DESCRIPTION)?.toString()?.trim();
            const incidentPriority = formData.get(FORM_INCIDENT_PRIORITY)?.toString()?.trim();
            //const incidentAssignees = formData.get(FORM_INCIDENT_ASSIGNEES)?.toString()?.trim();

            if (incidentName && incidentDescription && projectId) {
                const createdIncidentId = await Api.incidents.projectsProjectIdIncidentsPost({
                    projectId: projectId,
                    createIncidentRequest: {
                        title: incidentName,
                        description: incidentDescription,
                        // categoryId: undefined, ?
                        priority: incidentPriority as IncidentPriority,
                        // primaryAssigneeId: undefined
                    }
                }).catch(() => null);

                if (createdIncidentId){
                    return {ok: true};
                }
            }
        } else if (projectAction === FORM_ACTION_NEW_ROLE) {
            const roleName = formData.get(FORM_ROLE_NAME)?.toString()?.trim();
            const rolePermissions = formData.getAll(FORM_ROLE_PERMISSION).map((permission) => permission.toString());

            if (projectId && roleName) {
                const canAssignToProjects = rolePermissions.includes(PERM_ASSIGN_TO_PROJECT);
                const canChangeRoles = rolePermissions.includes(PERM_CHANGE_ROLES);
                const canMakeRoles = rolePermissions.includes(PERM_MAKE_ROLES);
                const canChangeStatus = rolePermissions.includes(PERM_CHANGE_STATUS);
                const canAssignHelp = rolePermissions.includes(PERM_ASSIGN_HELP);
                const canHelp = rolePermissions.includes(PERM_HELP);
                const canWriteTickets = rolePermissions.includes(PERM_WRITE_TICKETS);

                const createdRoleId = await Api.roles.projectsProjectIdRolesPost({
                    projectId: projectId,
                    createRoleRequest: {
                        name: roleName,
                        permissions: {
                            canAssignHelp: canAssignHelp,
                            canChangeRoles: canChangeRoles,
                            canMakeRoles: canMakeRoles,
                            canHelp: canHelp,
                            canAssignPeopleToProject: canAssignToProjects,
                            canChangeStatus: canChangeStatus,
                            canWriteTickets: canWriteTickets,
                        }
                    }
                }).catch(() => null);

                if (createdRoleId) {
                    return {ok: true};
                }
            }
        }
    }

    return {ok: false};
}

export const dashboardIncidentsAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    const projectAction = formData.get(FORM_ACTION)?.toString();
    if (!projectAction) {
        return {ok: false};
    }

    return {ok: true};
}
