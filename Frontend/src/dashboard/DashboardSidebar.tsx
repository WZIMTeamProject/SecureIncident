import {Link, useLoaderData, useParams} from "react-router";
import type {AuthState} from "../data/auth.ts";
import {useEffect, useState} from "react";
import type {Incident, Organization, Project} from "../data/project.ts";

export default function DashboardSidebar() {
    const auth = useLoaderData<AuthState>();
    const urlParams = useParams();

    const selectedProject = urlParams["projectId"];
    const selectedIncident = urlParams["incidentId"];

    const [userOrganization, setUserOrganization] = useState<Organization | null>();
    const [userProjects, setUserProjects] = useState<Project[]>();
    const [userIncidents, setUserIncidents] = useState<Incident[]>();

    useEffect(() => {
        auth.getOrganization().then((fetchedOrganization) => {
            setUserOrganization(() => fetchedOrganization);
        })
    }, [auth]);

    useEffect(() => {
        auth.getProjects().then((fetchedProjects) => {
            setUserProjects(() => fetchedProjects);
        });
    }, [auth]);

    useEffect(() => {
        auth.getReportedIncidents().then((assignedIncidents) => {
            setUserIncidents(() => assignedIncidents);
        });
    }, [auth]);

    return (
        <div className="w-full max-w-md shrink-0
                    bg-(--color-si-card-bg)
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">

            <OrganizationLink organization={userOrganization}/>
            <br/>
            <ProjectLinks projects={userProjects} selected={selectedProject}/>
            <br/>
            <IncidentLinks incidents={userIncidents} selected={selectedIncident}/>
            <br/>
        </div>
    );
}

function OrganizationLink({organization}: { organization: Organization | null | undefined }) {
    if (organization === undefined) {
        return <LoadingText/>;
    }

    return <>
        <h1 className="text-xl font-bold text-(--color-si-label)">
            Moja Organizacja
        </h1>
        <hr className="border-(--color-si-label)"/>

        <h2 className="p-1 overflow-x-clip">
            <Link to="/dashboard" className="hover:underline font-medium text-lg text-(--color-si-input-text)">
                {organization?.name ?? "- Brak -"}
            </Link>
        </h2>
    </>;
}

function ProjectLinks({projects, selected}: { projects: Project[] | undefined, selected?: string }) {
    if (projects === undefined) {
        return <LoadingText/>;
    }

    const projectLinks = projects.map((project) => {
        return <h2 className="overflow-x-clip">
            <Link
                to={`/dashboard/project/${project.id}`}
                className={`hover:underline text-lg text-(--color-si-input-text)
                    ${selected && project.id == selected ? "font-extrabold" : "font-medium"}`}>
                {project.name}
            </Link>
        </h2>;
    });

    if (projectLinks.length == 0) {
        projectLinks.push(
            <h2 className="font-medium text-lg text-(--color-si-input-text) italic"> - Brak - </h2>
        );
    }

    return <>
        <h1 className="text-xl font-bold text-(--color-si-label)">
            Moje Projekty ({projects.length})
        </h1>
        <hr className="border-(--color-si-label)"/>

        <div className="flex flex-col p-1 gap-1">
            {projectLinks}
        </div>
    </>;
}

function IncidentLinks({incidents, selected}: { incidents: Incident[] | undefined, selected?: string }) {
    if (incidents === undefined) {
        return <LoadingText/>;
    }

    const incidentLinks = incidents.map((incident) => {
        return <Link
            to={`/dashboard/incident/${incident.id}`}
            className={`hover:underline text-lg text-(--color-si-input-text)
                ${selected && incident.id == selected ? "font-extrabold" : "font-medium"}`}>
            {incident.title}
        </Link>
    });

    if (incidentLinks.length == 0) {
        incidentLinks.push(
            <h2 className="font-medium text-lg text-(--color-si-input-text) italic"> - Brak - </h2>
        );
    }

    return <>
        <h1 className="text-xl font-bold text-(--color-si-label)">
            Moje Incydenty ({incidents.length})
        </h1>
        <hr className="border-(--color-si-label)"/>

        <div className="flex flex-col p-1 gap-1">
            {incidentLinks}
        </div>
    </>;
}

function LoadingText() {
    return <h2 className="font-medium text-lg text-(--color-si-input-text)">
        Wczytywanie...
    </h2>;
}
