import type {Project} from "../../data/project.ts";
import * as React from "react";
import {useRef, useState} from "react";
import type {ProjectInfo} from "../SIProject.tsx";
import {useFetcher} from "react-router";
import type {RoleResponse, UserSearchResponse, UserSearchResult} from "../../api";
import {Popup} from "../../components/Popup.tsx";
import {FORM_ACTION, FormActions, ProjectForms} from "../forms.ts";
import Api from "../../data/Api.ts";

export function MemberList({show, project, projectInfo}: {
    show: boolean,
    project?: Project,
    projectInfo?: ProjectInfo
}) {
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const hidePopup = () => setShowPopup(false);

    const disableButtons: boolean = project === undefined;
    const members = projectInfo?.members;

    const canAddUsers = projectInfo?.myRole?.permissions.canAssignPeopleToProject ?? false;

    return (
        <div hidden={!show} className={"flex-1"}>
            {
                project && projectInfo && canAddUsers
                    ? <InviteToProjectPopup show={showPopup} onHide={hidePopup} project={project}
                                            projectInfo={projectInfo}/>
                    : undefined
            }

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl rounded-tl-none shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll text-(--color-si-input-text)">
                {
                    members?.map((member) => {
                        return <p key={member.userId}>
                            {member.username} - {member.roleName}
                        </p>;
                    }) ?? <h1>Ładowanie...</h1>
                }
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    onClick={() => setShowPopup(true)}
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

function InviteToProjectPopup({show, onHide, project, projectInfo}: {
    show: boolean,
    onHide: () => void,
    project: Project,
    projectInfo: ProjectInfo
}) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [pendingHide, setPendingHide] = useState<boolean>(false);
    const [selectedRole, setSelectedRole] = useState<RoleResponse | null>(null);
    const [searchResponse, setSearchResponse] = useState<UserSearchResponse | null>(null);

    const [selectedUser, setSelectedUser] = useState<UserSearchResult | null>();

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        setSelectedRole(null);
        setSelectedUser(null);
        onHide();
    }

    const userNameRef = useRef<HTMLInputElement>(null);
    const roleRef = useRef<HTMLSelectElement>(null);

    const roleOptions = projectInfo.roles.map((role) => {
        return <option key={role.id} value={role.id}>{role.name}</option>;
    });

    function searchFormAction(formData: FormData) {
        const query = formData.get("query")?.toString();

        if (query) {
            Api.users.usersSearchGet({query: query}).then(
                results => setSearchResponse(results),
                () => setSearchResponse(null)
            );
        } else {
            setSearchResponse(null);
        }

        setSelectedUser(null);
    }

    return (
        <Popup show={show} className={"w-full max-w-4xl"}>
            <h1 className="text-3xl font-bold text-(--color-si-label) mb-3">
                Dodawanie użytkowników do projektu {project.name}.
            </h1>

            <div className={"flex gap-6"}>
                <form
                    action={searchFormAction}
                    className={`gap-1 flex-1 border border-(--color-si-input-border) rounded-lg
                        px-3 py-2.5 transition-colors`}>

                    <input
                        className={"rounded-sm w-full outline-none text-sm text-(--color-si-input-text)"}
                        placeholder="Wyszukaj..."
                        name="query"
                        type="text"/>

                    <hr className={"my-1.5 border-(--color-si-input-border)"}/>

                    <div className={"flex-1 text-md h-64 w-full overflow-y-scroll"}>
                        {
                            searchResponse?.users.map((user) => {
                                return <p
                                    onClick={() => setSelectedUser(user)}
                                    key={user.id}
                                    className={`hover:underline cursor-pointer ${selectedUser?.id === user.id ? "font-bold" : ""}`}>
                                    {user.username}
                                </p>;
                            })
                        }
                    </div>
                </form>

                <div className={"border-l border-(--color-si-label) my-1.5"}/>

                <div className={"flex-1"}>
                    <fetcher.Form
                        className={"flex flex-col gap-3"}
                        method="POST"
                        onSubmit={() => setPendingHide(true)}>

                        <div className="flex flex-col gap-1.5">
                            <label htmlFor={ProjectForms.UserRole}
                                   className="text-sm font-medium text-(--color-si-label)">
                                Podaj rolę:
                            </label>

                            <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                                <select
                                    ref={roleRef}
                                    required={true}
                                    defaultValue={""}
                                    name={ProjectForms.UserRole}
                                    onChange={(ev) => {
                                        const roleId = ev.currentTarget.value;
                                        const role = projectInfo.roles.find(
                                            (role) => role.id === roleId
                                        );

                                        setSelectedRole(role ?? null);
                                    }}
                                    className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)">

                                    <option disabled={true} hidden={true} value="">
                                        Wybierz rolę dla użytkownika...
                                    </option>

                                    {roleOptions}
                                </select>
                            </div>
                        </div>

                        <PermissionList role={selectedRole ?? undefined}/>

                        <div className="flex items-center justify-between">
                            <button
                                disabled={busy}
                                onClick={() => {
                                    userNameRef.current = null;
                                    roleRef.current = null;
                                    setSelectedRole(null);
                                    setSelectedUser(null);
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
                                value={busy ? "Dodawanie..." : "Dodaj"}
                                disabled={busy}
                                className="px-6 py-2
                                    bg-(--color-si-btn)
                                    hover:bg-(--color-si-btn-hover) shadow-lg
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                            />
                        </div>

                        <input
                            required={true}
                            name={ProjectForms.UserName}
                            type="hidden"
                            value={selectedUser?.id}/>
                        <input
                            name={ProjectForms.ProjectId}
                            type="hidden"
                            value={project.id}/>
                        <input
                            name={FORM_ACTION}
                            type="hidden"
                            value={FormActions.InviteUser}/>
                    </fetcher.Form>
                </div>
            </div>
        </Popup>
    );
}

function PermissionList({role}: { role?: RoleResponse }) {
    const disabledPermissionStyle: string = "line-through italic font-medium text-gray-400 dark:text-gray-600";

    return <div className="flex flex-col gap-1.5">
        <h3 className="text-sm font-medium text-(--color-si-label)">
            Użytkownik będzie mógł:
        </h3>

        <div className="flex flex-col gap-y-2
                border border-(--color-si-input-border)
                rounded-lg px-6 py-2.5
                bg-(--color-si-input-bg) transition-colors">
            <ul className={`text-sm font-semibold text-green-600 dark:text-green-500 list-disc`}>
                <li className={role?.permissions.canWriteTickets ? undefined : disabledPermissionStyle}>
                    Zgłaszać incydenty
                </li>
                <li className={role?.permissions.canMakeRoles ? undefined : disabledPermissionStyle}>
                    Tworzyć role
                </li>
                <li className={role?.permissions.canHelp ? undefined : disabledPermissionStyle}>
                    Pomagać w incydentach
                </li>
                <li className={role?.permissions.canAssignHelp ? undefined : disabledPermissionStyle}>
                    Przypisywać pomocników
                </li>
                <li className={role?.permissions.canChangeRoles ? undefined : disabledPermissionStyle}>
                    Edytować role
                </li>
                <li className={role?.permissions.canChangeStatus ? undefined : disabledPermissionStyle}>
                    Zmieniać status incydentów
                </li>
                <li className={role?.permissions.canAssignPeopleToProject ? undefined : disabledPermissionStyle}>
                    Przypisywać użytkowników do projektów
                </li>
            </ul>
        </div>
    </div>;
}
