import * as React from "react";
import {useContext, useEffect, useRef, useState} from "react";
import type {Project} from "../data/project.ts";
import {Link, useFetcher, useParams} from "react-router";
import Api from "../data/Api.ts";
import {FORM_ACTION, FormActions, ProjectForms, UserPermissions} from "./forms.ts";
import {Popup} from "../components/Popup.tsx";
import type {IncidentSummary, ProjectMemberResponse, RoleResponse} from "../api";
import {AuthUserContext} from "../data/auth.ts";

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

type ProjectInfo = {
    incidents: IncidentSummary[];
    members: ProjectMemberResponse[];
    roles: RoleResponse[];
    myRole?: RoleResponse;
};

async function fetchProjectInfo(userId: string, projectId: string): Promise<ProjectInfo> {
    const incidentsPromise = Api.incidents.projectsProjectIdIncidentsGet({
        projectId: projectId,
        limit: 10
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

function IncidentList({show, project, projectInfo}: { show: boolean, project?: Project, projectInfo?: ProjectInfo }) {
    const [shownPopup, setShownPopup] = useState<ShownPopup>(null);
    const hidePopup = () => setShownPopup(null);

    const disableButtons: boolean = project === undefined;
    const incidents = projectInfo?.incidents;

    const canCreateIncidents = projectInfo?.myRole?.permissions.canWriteTickets ?? false;

    return (
        <div hidden={!show}>
            {
                project && canCreateIncidents
                    ? <NewIncidentPopup show={shownPopup == "new_incident"} onHide={hidePopup} project={project}/>
                    : undefined
            }

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl rounded-tl-none shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll text-(--color-si-input-text)">
                {
                    incidents?.map((incident) => {
                        return <IncidentEntry incident={incident}/>;
                    }) ?? <h1>Ładowanie...</h1>
                }
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    disabled={disableButtons || !canCreateIncidents}
                    title={canCreateIncidents ? undefined : "Nie masz uprawnień do wykonania tej czynności"}
                    onClick={() => setShownPopup("new_incident")}
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        disabled:opacity-60 text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Zgłoś nowy incydent
                </button>
            </div>
        </div>
    );
}

function IncidentEntry({incident}: { incident: IncidentSummary }) {
    return <div>
        <Link to={`/dashboard/incident/${incident.id}`} className={"hover:underline"}>
            {incident.title} - {incident.id}
        </Link>
    </div>
}

function MemberList({show, project, projectInfo}: { show: boolean, project?: Project, projectInfo?: ProjectInfo }) {
    const disableButtons: boolean = project === undefined;
    const members = projectInfo?.members;

    const canAddUsers = projectInfo?.myRole?.permissions.canAssignPeopleToProject ?? false;

    return (
        <div hidden={!show} className={"flex-1"}>
            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl rounded-tl-none shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll text-(--color-si-input-text)">
                {
                    members?.map((member) => {
                        return <p>
                            {member.username} - {member.roleName}
                        </p>;
                    }) ?? <h1>Ładowanie...</h1>
                }
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    disabled={disableButtons || !canAddUsers}
                    title={canAddUsers ? undefined : "Nie masz uprawnień do wykonania tej czynności"}
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        disabled:opacity-60 text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj użytkownika do projektu
                </button>
            </div>
        </div>
    )
}

function RoleList({show, project, projectInfo}: { show: boolean, project?: Project, projectInfo?: ProjectInfo }) {
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const hidePopup = () => setShowPopup(false);

    const disableButtons: boolean = project === undefined;
    const roles = projectInfo?.roles;

    const canCreateRoles = projectInfo?.myRole?.permissions.canMakeRoles ?? false;

    return (
        <div hidden={!show} className={"flex-1"}>
            {
                project && canCreateRoles
                    ? <NewRolePopup show={showPopup} onHide={hidePopup} project={project}/>
                    : undefined
            }

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl rounded-tl-none shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll text-(--color-si-input-text)">
                {
                    roles?.map((role) => {
                        return <p>
                            {role.name}
                        </p>;
                    }) ?? <h1>Ładowanie...</h1>
                }
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    onClick={() => setShowPopup(true)}
                    disabled={disableButtons || !canCreateRoles}
                    title={canCreateRoles ? undefined : "Nie masz uprawnień do wykonania tej czynności"}
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        disabled:opacity-60 text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Utwórz nową rolę
                </button>
            </div>
        </div>
    )
}

type ShownPopup = "new_incident" | null;

function NewIncidentPopup({show, onHide, project}: { show: boolean, onHide: () => void, project: Project }) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [pendingHide, setPendingHide] = useState<boolean>(false);

    const incidentNameRef = useRef<HTMLInputElement>(null);
    const incidentDescriptionRef = useRef<HTMLInputElement>(null);
    const incidentPriorityRef = useRef<HTMLSelectElement>(null);
    const incidentAssigneesRef = useRef<HTMLInputElement>(null);

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        onHide();
    }

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Zgłoszenie nowego incydentu w projekcie "{project.name}":
                </h1>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.IncidentName} className="text-sm font-medium text-(--color-si-label)">
                        Podaj nazwę incydentu:
                    </label>
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={incidentNameRef}
                            type="text"
                            required={true}
                            name={ProjectForms.IncidentName}
                            placeholder="Nazwa"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.IncidentDescription}
                           className="text-sm font-medium text-(--color-si-label)">
                        Podaj opis incydentu:
                    </label>
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={incidentDescriptionRef}
                            type="text"
                            required={true}
                            name={ProjectForms.IncidentDescription}
                            placeholder="Opis"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.IncidentPriority}
                           className="text-sm font-medium text-(--color-si-label)">
                        Podaj odpowiedni priorytet:
                    </label>
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <select
                            ref={incidentPriorityRef}
                            required={true}
                            name={ProjectForms.IncidentPriority}
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)">

                            <option value={"LOW"}>Niski</option>
                            <option value={"MEDIUM"}>Średni</option>
                            <option value={"HIGH"}>Wysoki</option>
                            <option value={"CRITICAL"}>Krytyczny</option>
                        </select>
                    </div>
                </div>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.IncidentAssignees}
                           className="text-sm font-medium text-(--color-si-label)">
                        Przypisz użytkownika:
                    </label>
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={incidentAssigneesRef}
                            type="text"
                            name={ProjectForms.IncidentAssignees}
                            placeholder="Wpisz nazwę użytkownika lub rolę (oddziel użytkowników przecinkiem)"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        disabled={busy}
                        onClick={() => {
                            incidentNameRef.current = null;
                            incidentDescriptionRef.current = null;
                            incidentPriorityRef.current = null;
                            incidentAssigneesRef.current = null;
                            onHide();
                        }}
                        className="px-6 py-2
                                bg-(--color-si-btn-error)
                                hover:bg-(--color-si-btn-error-hover) shadow-lg
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Dodawanie..." : "Dodaj Incydent"}
                        disabled={busy}
                        className="px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={ProjectForms.ProjectId}
                    type="hidden"
                    value={project.id}/>
                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FormActions.NewIncident}/>
            </fetcher.Form>
        </Popup>
    );
}

function NewRolePopup({show, onHide, project}: { show: boolean, onHide: () => void, project: Project }) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [pendingHide, setPendingHide] = useState<boolean>(false);

    const roleNameRef = useRef<HTMLInputElement>(null);
    const rolePermWriteTicketRef = useRef<HTMLInputElement>(null);
    const rolePermHelpRef = useRef<HTMLInputElement>(null);
    const rolePermAssignHelpRef = useRef<HTMLInputElement>(null);
    const rolePermChangeStatusRef = useRef<HTMLInputElement>(null);
    const rolePermMakeRoleRef = useRef<HTMLInputElement>(null);
    const rolePermChangeRoleRef = useRef<HTMLInputElement>(null);
    const rolePermAssignToProjectRef = useRef<HTMLInputElement>(null);

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        onHide();
    }

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Tworzenie nowej roli w projekcie {project.name}.
                </h1>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.RoleName} className="text-sm font-medium text-(--color-si-label)">
                        Podaj nazwę roli:
                    </label>
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={roleNameRef}
                            type="text"
                            required={true}
                            name={ProjectForms.RoleName}
                            placeholder="Nazwa"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.RolePermissions}
                           className="text-sm font-medium text-(--color-si-label)">
                        Pozwolenia:
                    </label>

                    <div className="flex flex-wrap gap-y-2
                                text-sm font-medium text-(--color-si-label)
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermWriteTicketRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.WriteTickets}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Zgłaszanie incydentów
                        </div>

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermHelpRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.Help}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Pomaganie
                        </div>

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermAssignHelpRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.AssignHelp}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Przypisywanie pomocników
                        </div>

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermChangeStatusRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.ChangeStatus}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Zmiana statusu
                        </div>

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermMakeRoleRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.MakeRoles}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Tworzenie ról
                        </div>

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermChangeRoleRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.ChangeRoles}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Edytowanie ról
                        </div>

                        <div className="flex gap-1 items-center flex-1/2">
                            <input
                                type="checkbox"
                                ref={rolePermAssignToProjectRef}
                                name={ProjectForms.RolePermissions}
                                value={UserPermissions.AssignToProject}
                                className="w-4 h-4 bg-(--color-si-input-bg) accent-(--color-si-btn) cursor-pointer"
                            />
                            Przypisywanie do projektów
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        disabled={busy}
                        onClick={() => {
                            roleNameRef.current = null;
                            rolePermWriteTicketRef.current = null;
                            rolePermHelpRef.current = null;
                            rolePermAssignHelpRef.current = null;
                            rolePermChangeStatusRef.current = null;
                            rolePermMakeRoleRef.current = null;
                            rolePermChangeRoleRef.current = null;
                            rolePermAssignToProjectRef.current = null;
                            onHide();
                        }}
                        className="px-6 py-2
                                bg-(--color-si-btn-error)
                                hover:bg-(--color-si-btn-error-hover) shadow-lg
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Tworzenie..." : "Utwórz"}
                        disabled={busy}
                        className="px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={ProjectForms.ProjectId}
                    type="hidden"
                    value={project.id}/>
                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FormActions.NewRole}/>
            </fetcher.Form>
        </Popup>
    );
}