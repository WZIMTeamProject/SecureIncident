import {Link, useLoaderData} from "react-router";
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

            <OrganizationLink organization={userOrganization}/><br/>

            <h1>Moje Projekty</h1>
            <hr/>

            <ProjectLinks projects={userProjects}/><br/>

            <h1>Moje Incydenty</h1>
            <hr/>

            <IncidentLinks incidents={userIncidents}/><br/>
        </div>
    );
}

function OrganizationLink({organization}: { organization: Organization | null | undefined }) {
    if (organization === undefined) {
        return <h2>Wczytywanie...</h2>;
    }

    return <h2>
        <Link to="/dashboard">{organization?.name ?? "- Brak -"}</Link>
    </h2>;
}

function ProjectLinks({projects}: { projects: Project[] | undefined }) {
    if (projects === undefined) {
        return <h2>Wczytywanie...</h2>;
    }

    const projectLinks = projects.map((project) => {
        return <h2><Link to={`/dashboard/project/${project.id}`}>{project.name}</Link></h2>;
    });

    return <>{projectLinks}</>;
}

function IncidentLinks({incidents}: { incidents: Incident[] | undefined }) {
    if (incidents === undefined) {
        return <h2>Wczytywanie...</h2>;
    }

    return <>
        {incidents.map((incident) => <h2>{incident.title}</h2>)}
    </>
}