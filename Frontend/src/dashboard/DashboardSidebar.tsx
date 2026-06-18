import {useLoaderData} from "react-router";
import type {AuthState} from "../data/auth.ts";
import {useEffect, useState} from "react";
import type {Incident, Organization, Project} from "../data/project.ts";

export default function DashboardSidebar() {
    const auth = useLoaderData<AuthState>();

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
        auth.getAssignedIncidents().then((assignedIncidents) => {
            setUserIncidents(() => assignedIncidents);
        });
    }, [auth]);

    return (
        <div className="w-full max-w-md
                    bg-(--color-si-card-bg)
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">
            <h1>Moja Organizacja</h1>
            <hr/>

            <OrganizationLink organization={userOrganization}/>

            <h1>Moje Projekty</h1>
            <hr/>

            <ProjectLinks projects={userProjects}/>

            <h1>Moje Incydenty</h1>
            <hr/>

            <IncidentLinks incidents={userIncidents}/>
        </div>
    );
}

function OrganizationLink({ organization } : { organization: Organization | null | undefined }) {
    return <h2>
        {organization === undefined ? "Wczytywanie..." : (organization?.name ?? "- Brak -") }
    </h2>;
}

function ProjectLinks({ projects } : { projects: Project[] | undefined }) {
    return <>
        {projects?.map((project) => project.name) ?? "Wczytywanie..." }
    </>;
}

function IncidentLinks({ incidents } : { incidents: Incident[] | undefined }) {
    return <>
        {incidents?.map((incident) => incident.title) ?? "Wczytywanie..." }
    </>
}