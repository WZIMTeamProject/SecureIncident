import type {Project} from "../../data/project.ts";
import {useRef, useState} from "react";
import * as React from "react";
import type {ProjectInfo} from "../SIProject.tsx";
import {useFetcher} from "react-router";
import type {RoleResponse} from "../../api";
import {Popup} from "../../components/Popup.tsx";
import {FORM_ACTION, FormActions, ProjectForms} from "../forms.ts";

export function MemberList({show, project, projectInfo}: { show: boolean, project?: Project, projectInfo?: ProjectInfo }) {
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const hidePopup = () => setShowPopup(false);

    const disableButtons: boolean = project === undefined;
    const members = projectInfo?.members;

    const canAddUsers = projectInfo?.myRole?.permissions.canAssignPeopleToProject ?? false;

    return (
        <div hidden={!show} className={"flex-1"}>
            {
                project && projectInfo && canAddUsers
                    ? <InviteToProjectPopup show={showPopup} onHide={hidePopup} project={project} projectInfo={projectInfo}/>
                    : undefined
            }

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

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        setSelectedRole(null);
        onHide();
    }

    const userNameRef = useRef<HTMLInputElement>(null);
    const roleRef = useRef<HTMLSelectElement>(null);

    const roleOptions = projectInfo.roles.map((role) => {
        return <option key={role.id} value={role.id}>{role.name}</option>;
    });

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Dodawanie użytkowników do projektu {project.name}.
                </h1>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.UserName} className="text-sm font-medium text-(--color-si-label)">
                        Podaj nazwę użytkownika:
                    </label>
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={userNameRef}
                            type="text"
                            required={true}
                            name={ProjectForms.UserName}
                            placeholder="Nazwa"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5 my-3">
                    <label htmlFor={ProjectForms.RoleName}
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
                            name={ProjectForms.RoleName}
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

                    {selectedRole ? <PermissionList role={selectedRole}/> : undefined}
                </div>

                <div className="flex items-center justify-between">
                    <button
                        disabled={busy}
                        onClick={() => {
                            roleRef.current = null;
                            setSelectedRole(null);
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
                    name={ProjectForms.ProjectId}
                    type="hidden"
                    value={project.id}/>
                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FormActions.InviteUser}/>
            </fetcher.Form>
        </Popup>
    );
}

function PermissionList({role}: {role: RoleResponse}) {
    return <div className="flex flex-col gap-1.5 p-1.5">
        <h3 className="text-sm font-medium text-(--color-si-label)">
            Użytkownik będzie mógł:
        </h3>
        <div className="flex flex-col gap-y-2
                                text-sm font-medium text-(--color-si-input-text)
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
            <ul>
                <li>{role.permissions.canWriteTickets ? "Zgłaszać incydenty" : undefined}</li>
                <li>{role.permissions.canMakeRoles ? "Tworzyć role" : undefined}</li>
                <li>{role.permissions.canHelp ? "Pomagać" : undefined}</li>
                <li>{role.permissions.canChangeRoles ? "Edytować role" : undefined}</li>
                <li>{role.permissions.canChangeStatus ? "Zmieniać status indydentów" : undefined}</li>
                <li>{role.permissions.canAssignHelp ? "Przypisywać pomocników" : undefined}</li>
            </ul>
        </div>
    </div>;
}
