import type {IncidentLogType, IncidentPriority, IncidentStatus, ProjectScope} from "../api";

export interface Project {
    id: string;
    name: string;
    description?: string;
    organizationId?: string;
    scope: ProjectScope;
}

export interface Organization {
    id: string;
    name: string;
    description?: string;
}

export interface Incident {
    id: string;
    projectId?: string;
    title: string;
    description?: string;
    categoryId?: string;
    priority: IncidentPriority;
    status: IncidentStatus;
    primaryAssigneeId?: string;
    reportDate: Date; // Could use new Temporal api if we decided to abandon Safari users in the dust.
}

export interface IncidentHistoryEntry {
    id: string;
    incidentId: string;
    type: IncidentLogType,
    createdAt: Date;
    actorId: string;
    comment?: string;
    oldValue?: string;
    newValue?: string;
}

/**
 * Hardcoded sample projects for local UI development. Returns an empty list in production.
 */
export function getDummyProjects(): Project[] {
    if (import.meta.env.DEV) {
        return [
            {
                name: "Projekt Testowy",
                description: "To jest bardzo ważny projekt",
                id: "0000-0000-0000-0001",
                scope: "ORGANIZATION",
                organizationId: "0000-0000-0000-0001"
            },
            {
                name: "Projekt Bez Opisu",
                id: "0000-0000-0000-0002",
                scope: "ORGANIZATION",
                organizationId: "0000-0000-0000-0001"
            },
            {
                name: "Projekt Bez Organizacji",
                description: "Ja nie mam organizacji",
                id: "0000-0000-0000-0003",
                scope: "PRIVATE",
            },
            {
                name: "Jeszcze Jakiś Projekt",
                id: "0000-0000-0000-0004",
                scope: "ORGANIZATION",
                organizationId: "0000-0000-0000-0002"
            },
        ]
    } else {
        return [];
    }
}
