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
            <div className="p-3">
                <h1 className="text-2xl font-bold">{project.name}</h1>
                <p className="text-md text-gray-600 italic font-normal">{project.description ?? "Brak opisu"}</p>
            </div>

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll">
                TODO: Incidents go here
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Zgłoś nowy incydent
                </button>

                <button
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj użytkownika do projektu
                </button>
            </div>
        </div>
    );
}