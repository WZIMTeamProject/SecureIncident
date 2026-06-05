import type {IncidentsHistoryGetTypeEnum, ProjectsGetScopeEnum} from "../api";

export type ProjectScope = ProjectsGetScopeEnum;

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

export type IncidentPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type IncidentStatus = "NEW" | "PROBLEM_IS_BEING_SOLVED" | "RESOLVED" | "CLOSED" | "REJECTED";
export type IncidentHistoryType = IncidentsHistoryGetTypeEnum; // I have no clue why this is the only one actually documented.

export interface Incident {
    id: string;
    title: string;
    categoryId?: string;
    priority: IncidentPriority;
    status: IncidentStatus;
    primaryAssigneeId?: string;
    reportDate: Date; // Could use new Temporal api if we decided to abandon Safari users in the dust.
}

export interface IncidentHistoryEntry {
    id: string;
    incidentId: string;
    type: IncidentHistoryType;
    createdAt: Date;
    actorId: string;
    comment?: string;
    oldValue?: string;
    newValue?: string;
}

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