export enum OrganizationForms {
    OrganizationName = "organization_name",
    ProjectName = "project_name",
    Description = "description",
    InviteCount = "invite_count",
    InviteToken = "invite_token",
}

export enum ProjectForms {
    IncidentName = "incident_name",
    IncidentDescription = "incident_description",
    IncidentPriority = "incident_priority",
    IncidentAssignees = "incident_assignees",
    ProjectId = "project_id",
    RoleName = "role_name",
    RolePermissions = "role_permissions",
    UserName = "user_name",
    UserRole = "user_role",
}

export enum IncidentForms {
    InviteName = "invite_name",
}

export const FORM_ACTION = "action";

export enum FormActions {
    NewProject = "new_project",
    InviteUser = "invite_user",
    CreateOrganization = "create_organization",
    DeleteOrganization = "delete_organization",
    JoinOrganization = "join_organization",
    NewIncident = "new_incident",
    NewRole = "new_role",
}

export enum UserPermissions {
    WriteTickets = "write_tickets",
    Help = "help",
    AssignHelp = "assign_help",
    ChangeStatus = "change_status",
    MakeRoles = "make_roles",
    ChangeRoles = "change_roles",
    AssignToProject = "assign_to_project",
}