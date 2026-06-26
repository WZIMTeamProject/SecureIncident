import {type ActionFunction} from "react-router";
import {FORM_ACTION, FormActions, OrganizationForms, ProjectForms, UserPermissions} from "./forms.ts";
import Api from "../data/Api.ts";
import type {IncidentPriority} from "../api";

export const dashboardOrganizationAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    const organizationAction = formData.get(FORM_ACTION)?.toString();
    if (!organizationAction) {
        return {ok: false};
    }

    if (request.method === "POST") {
        if (organizationAction === FormActions.NewProject) {
            const projectName = formData.get(OrganizationForms.ProjectName)?.toString()?.trim();
            const projectDescription = formData.get(OrganizationForms.Description)?.toString()?.trim();

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
        } else if (organizationAction === FormActions.InviteUser) {
            const maxUses = Number(formData.get(OrganizationForms.InviteCount));

            if (maxUses > 0) {
                const inviteResponse = await Api.organization.organizationInvitesPost({
                    createOrgInviteRequest: {
                        expiresAt: undefined,
                        maxUses: maxUses,
                    }
                }).catch(() => null);

                if (inviteResponse) {
                    return {
                        ok: true,
                        token: inviteResponse.token,
                        inviteUrl: inviteResponse.inviteUrl,
                    };
                }
            }
        } else if (organizationAction === FormActions.CreateOrganization) {
            const organizationName = formData.get(OrganizationForms.OrganizationName)?.toString()?.trim();
            const organizationDescription = formData.get(OrganizationForms.Description)?.toString()?.trim();

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
        } else if (organizationAction === FormActions.JoinOrganization) {
            const token = formData.get(OrganizationForms.InviteToken)?.toString()?.trim();

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
        if (organizationAction === FormActions.DeleteOrganization) {
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

    const projectId = formData.get(ProjectForms.ProjectId)?.toString()?.trim();

    if (request.method === "POST") {
        if (projectAction === FormActions.NewIncident) {
            const incidentName = formData.get(ProjectForms.IncidentName)?.toString()?.trim();
            const incidentDescription = formData.get(ProjectForms.IncidentDescription)?.toString()?.trim();
            const incidentPriority = formData.get(ProjectForms.IncidentPriority)?.toString()?.trim();
            // TODO: const incidentAssignees = ...

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

                if (createdIncidentId) {
                    return {ok: true};
                }
            }
        } else if (projectAction === FormActions.NewRole) {
            const roleName = formData.get(ProjectForms.RoleName)?.toString()?.trim();
            const rolePermissions = formData.getAll(ProjectForms.RolePermissions)
                .map((permission) => permission.toString());

            if (projectId && roleName) {
                const canAssignToProjects = rolePermissions.includes(UserPermissions.AssignToProject);
                const canChangeRoles = rolePermissions.includes(UserPermissions.ChangeRoles);
                const canMakeRoles = rolePermissions.includes(UserPermissions.MakeRoles);
                const canChangeStatus = rolePermissions.includes(UserPermissions.ChangeStatus);
                const canAssignHelp = rolePermissions.includes(UserPermissions.AssignHelp);
                const canHelp = rolePermissions.includes(UserPermissions.Help);
                const canWriteTickets = rolePermissions.includes(UserPermissions.WriteTickets);

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
