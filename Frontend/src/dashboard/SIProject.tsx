import {useEffect, useState} from "react";
import type {Project} from "../data/project.ts";
import {useParams} from "react-router";
import Api from "../data/Api.ts";

export function SIProject() {
    const urlParams = useParams();

    const [project, setProject] = useState<Project | null>();

    useEffect(() => {
        const projectId = urlParams["projectId"];

        if(projectId) {
            Api.projects.projectsProjectIdGet({
                projectId: projectId,
            }).then((projectResponse) => {
                setProject({
                    description: projectResponse.description ?? undefined,
                    id: projectResponse.id,
                    name: projectResponse.name,
                    scope: projectResponse.scope,
                    organizationId: projectResponse.organizationId ?? undefined,
                });
            }).catch(() => {
                setProject(null);
            });
        }
    }, [urlParams]);

    if (project === undefined) {
        return <div><LoadingMessage/></div>;
    }


    return (
        <div>
            {project === null ? "ERROR" : <ProjectView project={project}/>}
        </div>
    );
}

function LoadingMessage() {
    return <h1>Wczytywanie...</h1>;
}

function ProjectView({project}: { project: Project }) {
    return (
        <div>
            <p>{project.name} - {project.id}</p>
            <p>{project.description}</p>
        </div>
    );
}