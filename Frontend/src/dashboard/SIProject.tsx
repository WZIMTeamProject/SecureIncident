import * as React from "react";
import {useContext, useEffect, useState} from "react";
import type {Project} from "../data/project.ts";
import {useParams} from "react-router";
import Api from "../data/Api.ts";
import type {IncidentSummary, ProjectMemberResponse, RoleResponse} from "../api";
import {AuthUserContext} from "../data/auth.ts";
import {IncidentList, MemberList, RoleList} from "./project";

export function SIProject() {
    const urlParams = useParams();
    const [project, setProject] = useState<Project | null>();

    const projectId = urlParams["projectId"];

    if (project && project.id !== projectId) {
        if (projectId) {
            setProject(undefined);
        } else {
            setProject(null);
        }
    }

    useEffect(() => {
        if (projectId) {
            Api.projects.projectsProjectIdGet({
                projectId: projectId,
            }).then(
                (projectResponse) => {
                    setProject({
                        description: projectResponse.description ?? undefined,
                        id: projectResponse.id,
                        name: projectResponse.name,
                        scope: projectResponse.scope,
                        organizationId: projectResponse.organizationId ?? undefined,
                    });
                },
                () => setProject(null)
            );
        }
    }, [projectId]);

    return (
        <div>
            {project === null ? "ERROR" : <ProjectView project={project}/>}
        </div>
    );
}

export type ProjectInfo = {
    incidents: IncidentSummary[];
    members: ProjectMemberResponse[];
    roles: RoleResponse[];
    myRole?: RoleResponse;
};

async function fetchProjectInfo(userId: string, projectId: string): Promise<ProjectInfo> {
    const incidentsPromise = Api.incidents.projectsProjectIdIncidentsGet({
        projectId: projectId,
        limit: 10 // TODO: should be un-hardcoded
    });
    const membersPromise = Api.projects.projectsProjectIdMembersGet({
        projectId: projectId
    });
    const rolesPromise = Api.roles.projectsProjectIdRolesGet({
        projectId: projectId,
    });

    const [incidents, members, roles] = await Promise.all([incidentsPromise, membersPromise, rolesPromise]);

    const meAsMember = members.members.find(
        (member) => member.userId === userId
    );

    const projectInfo: ProjectInfo = {
        incidents: incidents.items,
        members: members.members,
        roles: roles.items,
    };

    if (meAsMember) {
        const myRoleId = meAsMember.roleId;
        projectInfo.myRole = roles.items.find((role) => role.id === myRoleId);
    }

    return projectInfo;
}

function ProjectView({project}: { project?: Project }) {
    const auth = useContext(AuthUserContext)!;

    const [projectInfo, setProjectInfo] = useState<ProjectInfo | undefined>(undefined);

    if (project === undefined && projectInfo !== undefined) {
        setProjectInfo(undefined);
    }

    useEffect(() => {
        let ignore = false;

        if (project) {
            fetchProjectInfo(auth.id, project.id).then(
                (projectInfo) => {
                    if (!ignore) {
                        setProjectInfo(projectInfo)
                    }
                },
                () => {
                    setProjectInfo({
                        incidents: [],
                        members: [],
                        roles: [],
                    })
                }
            );
        }

        return () => {
            ignore = true
        };
    }, [project, auth]);

    return (
        <div>
            <div className="p-3">
                <h1 className="text-2xl font-bold text-(--color-si-label)">
                    {project?.name ?? "Wczytywanie..."}
                </h1>
                <p className="text-md text-(--color-si-input-text) italic font-normal">
                    {project ? (project.description || "Brak opisu") : "..."}
                </p>
            </div>

            <div className="text-lg font-bold px-6 py-2 transition-colors duration-300
                bg-(--color-si-card-border) text-(--color-si-card-bg)
                rounded-t-lg w-fit shadow-lg">
                Incydenty
            </div>

            <IncidentList
                show={true}
                project={project}
                projectInfo={projectInfo}/>

            <div className="flex flex-row justify-center gap-3">
                <div className={"flex-1"}>
                    <div className="text-lg font-bold px-6 py-2 transition-colors duration-300
                        bg-(--color-si-card-border) text-(--color-si-card-bg)
                        rounded-t-lg w-fit shadow-lg">
                        Członkowie
                    </div>

                    <MemberList
                        show={true}
                        project={project}
                        projectInfo={projectInfo}/>
                </div>

                <div className={"flex-1"}>
                    <div className="text-lg font-bold px-6 py-2 transition-colors duration-300
                        bg-(--color-si-card-border) text-(--color-si-card-bg)
                        rounded-t-lg w-fit shadow-lg">
                        Role
                    </div>

                    <RoleList
                        show={true}
                        project={project}
                        projectInfo={projectInfo}/>
                </div>
            </div>
        </div>
    );
}