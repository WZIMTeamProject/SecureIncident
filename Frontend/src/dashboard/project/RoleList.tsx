import {useRef, useState} from "react";
import type {Project} from "../../data/project.ts";
import type {ProjectInfo} from "../SIProject.tsx";
import {useFetcher} from "react-router";
import {FORM_ACTION, FormActions, ProjectForms, UserPermissions} from "../forms.ts";
import {Popup} from "../../components/Popup.tsx";

export function RoleList({show, project, projectInfo}: { show: boolean, project?: Project, projectInfo?: ProjectInfo }) {
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
                        return <p key={role.id}>
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
