import {AuthUserContext} from "../data/auth.ts";
import {useContext, useEffect, useRef, useState} from "react";
import type {Organization, Project} from "../data/project.ts";
import {Popup} from "../components/Popup.tsx";
import {
    FORM_ACTION, FORM_ACTION_CREATE_ORGANIZATION, FORM_ACTION_DELETE_ORGANIZATION, FORM_ACTION_INVITE_USER,
    FORM_ACTION_NEW_PROJECT,
    FORM_INVITE_NAME, FORM_ORGANIZATION_DESCRIPTION, FORM_ORGANIZATION_NAME,
    FORM_PROJECT_DESCRIPTION,
    FORM_PROJECT_NAME
} from "./forms.ts";
import {useFetcher} from "react-router";

export function SIOrganization() {
    const auth = useContext(AuthUserContext)!;

    const [organization, setOrganization] = useState<Organization | null>();

    useEffect(() => {
        auth.getOrganization().then((value) => {
            setOrganization(() => value);
        });
    }, [auth]);

    if (organization === undefined) {
        return <div><LoadingMessage/></div>;
    }

    return (
        <div>
            {
                organization === null
                    ? <CreateOrganizationWidget/>
                    : <OrganizationView organization={organization}/>
            }
        </div>
    );
}

function LoadingMessage() {
    return <h1>Wczytywanie...</h1>;
}

function CreateOrganizationWidget() {
    const [shownPopup, setShownPopup] = useState<ShownCreateOrganizationPopup>(null);
    const hidePopup = () => setShownPopup(null)

    return (
        <div className="w-full flex gap-3 p-3 justify-end">
            <CreateOrganizationPopup show={shownPopup == "new_organization"} onHide={hidePopup}/>

            <button
                onClick={() => setShownPopup("new_organization")}
                className="px-6 py-2
                        bg-[var(--color-si-btn)]
                        hover:bg-[var(--color-si-btn-hover)] shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                Utwórz organizację
            </button>

            <button className="px-6 py-2
                        bg-[var(--color-si-btn)]
                        hover:bg-[var(--color-si-btn-hover)] shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                Dołącz do organizacji
            </button>
        </div>
    );
}

type ShownCreateOrganizationPopup = "new_organization" | "join_organization" | null;
type ShownOrganizationPopup = "new_project" | "invite_user" | "delete_organization" | null;

function OrganizationView({organization}: { organization: Organization }) {
    const auth = useContext(AuthUserContext)!;

    const [shownPopup, setShownPopup] = useState<ShownOrganizationPopup>(null);
    const hidePopup = () => setShownPopup(null)

    const [projects, setProjects] = useState<Project[] | undefined>();

    useEffect(() => {
        auth.getProjects("ORGANIZATION").then((orgProjects) => {
            setProjects(orgProjects);
        });
    }, [auth, organization]);

    return (
        <div>
            <NewProjectPopup show={shownPopup == "new_project"} onHide={hidePopup}/>
            <AddToOrganizationPopup show={shownPopup == "invite_user"} onHide={hidePopup}/>
            <DeleteOrganizationPopup show={shownPopup == "delete_organization"} onHide={hidePopup}/>

            <div className="p-3">
                <h1 className="text-2xl font-bold">{organization.name}</h1>
                <p className="text-md text-gray-600 italic font-normal">{organization.description ?? "Brak opisu"}</p>
            </div>

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll">
                {
                    projects?.map((project) => {
                        return <h1>{project.name} - {project.id}</h1>;
                    }) ?? <h1>Ładowanie...</h1>
                }
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    onClick={() => setShownPopup("new_project")}
                    className="px-6 py-2
                        bg-[var(--color-si-btn)]
                        hover:bg-[var(--color-si-btn-hover)] shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj nowy projekt
                </button>

                <button
                    onClick={() => setShownPopup("invite_user")}
                    className="px-6 py-2
                        bg-[var(--color-si-btn)]
                        hover:bg-[var(--color-si-btn-hover)] shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj użytkownika do organizacji
                </button>
            </div>

            <div className="w-full flex px-3 justify-end">
                <button
                    onClick={() => setShownPopup("delete_organization")}
                    className="px-6 py-2
                        bg-[var(--color-si-btn-error)]
                        hover:bg-[var(--color-si-btn-error-hover)] shadow-lg
                        text-white text-md font-semibold underline rounded-lg cursor-pointer transition-colors duration-200">
                    Usuń organizację
                </button>
            </div>
        </div>
    );
}

type PopupProps = { show: boolean, onHide: () => void };

function NewProjectPopup({show, onHide}: PopupProps) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [pendingHide, setPendingHide] = useState<boolean>(false);

    const projectNameRef = useRef<HTMLInputElement>(null);
    const projectDescriptionRef = useRef<HTMLInputElement>(null);

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        onHide();
    }

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold">
                    Nowy Projekt
                </h1>
                <h3 className="text-lg font-medium">
                    Podaj dane nowego projektu:
                </h3>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">
                        <input
                            ref={projectNameRef}
                            id={FORM_PROJECT_NAME}
                            type="text"
                            required={true}
                            name={FORM_PROJECT_NAME}
                            placeholder="Nazwa"
                            className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                        />
                    </div>

                    <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">
                        <input
                            ref={projectDescriptionRef}
                            id={FORM_PROJECT_DESCRIPTION}
                            type="text"
                            name={FORM_PROJECT_DESCRIPTION}
                            placeholder="Opis (opcjonalny)"
                            className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                        />
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        disabled={busy}
                        onClick={() => {
                            projectNameRef.current = null;
                            projectDescriptionRef.current = null;
                            onHide();
                        }}
                        className="px-6 py-2
                                bg-[var(--color-si-btn-error)]
                                hover:bg-[var(--color-si-btn-error-hover)] shadow-lg
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Zapisywanie..." : "Zapisz"}
                        disabled={busy}
                        className="px-6 py-2
                                    bg-[var(--color-si-btn)]
                                    hover:bg-[var(--color-si-btn-hover)] shadow-lg
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FORM_ACTION_NEW_PROJECT}/>
            </fetcher.Form>
        </Popup>
    );
}

function AddToOrganizationPopup({show, onHide}: PopupProps) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const usernameRef = useRef<HTMLInputElement>(null);

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST">
                <h1 className="text-3xl font-bold">
                    Dodaj do organizacji
                </h1>
                <h3 className="text-lg font-medium">
                    Możesz dodać nowego użytkownika do organizacji
                    ręcznie lub poprzez kod bądź link.
                </h3>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">
                        <input
                            ref={usernameRef}
                            id={FORM_INVITE_NAME}
                            type="text"
                            name={FORM_INVITE_NAME}
                            placeholder="Ręcznie (wpisz nazwę użytkownika)"
                            className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                        />
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        onClick={() => {
                            usernameRef.current = null;
                            onHide();
                        }}
                        className="px-6 py-2
                                bg-[var(--color-si-btn-error)]
                                hover:bg-[var(--color-si-btn-error-hover)] shadow-lg
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Zapisywanie..." : "Zapisz"}
                        disabled={busy}
                        className="px-6 py-2
                                    bg-[var(--color-si-btn)]
                                    hover:bg-[var(--color-si-btn-hover)] shadow-lg
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FORM_ACTION_INVITE_USER}/>
            </fetcher.Form>

        </Popup>
    );
}

function DeleteOrganizationPopup({show, onHide}: PopupProps) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="DELETE">
                <h1 className="text-3xl font-bold">
                    USUWANIE ORGANIZACJI
                </h1>

                <h3 className="text-lg font-medium mt-2 mb-4">
                    Czy na pewno chcesz usunąć organizację?
                    Usunie ją to bezpowrotnie z Twojego dashboardu razem z projektami!
                </h3>

                <div className="flex items-center justify-between">
                    <button
                        onClick={onHide}
                        className="px-6 py-2
                                bg-[var(--color-si-btn)]
                                hover:bg-[var(--color-si-btn-hover)] shadow-lg
                                text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        NIE, ANULUJ
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Usuwanie..." : "Tak, usuń"}
                        disabled={busy}
                        className="px-6 py-2
                                    bg-[var(--color-si-btn-error)]
                                    hover:bg-[var(--color-si-btn-error-hover)] shadow-lg
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FORM_ACTION_DELETE_ORGANIZATION}/>
            </fetcher.Form>
        </Popup>
    );
}

function CreateOrganizationPopup({show, onHide}: PopupProps) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [pendingHide, setPendingHide] = useState<boolean>(false);

    const organizationName = useRef<HTMLInputElement>(null);
    const organizationDescription = useRef<HTMLInputElement>(null);

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        onHide();
    }

    return (
        <Popup show={show} className={"w-full max-w-xl"} >
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold">
                    Utwórz nową organizację
                </h1>
                <h3 className="text-lg font-medium">
                    Wpisz nazwę organizacji:
                </h3>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">
                        <input
                            ref={organizationName}
                            required={true}
                            id={FORM_ORGANIZATION_NAME}
                            type="text"
                            name={FORM_ORGANIZATION_NAME}
                            placeholder="Nazwa organizacji"
                            className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                        />
                    </div>

                    <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">
                        <input
                            ref={organizationDescription}
                            id={FORM_ORGANIZATION_DESCRIPTION}
                            type="text"
                            name={FORM_ORGANIZATION_DESCRIPTION}
                            placeholder="Opis (opcjonalny)"
                            className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                        />
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        onClick={() => {
                            organizationName.current = null;
                            organizationDescription.current = null;
                            onHide();
                        }}
                        className="px-6 py-2
                                bg-[var(--color-si-btn-error)]
                                hover:bg-[var(--color-si-btn-error-hover)] shadow-lg
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Tworzenie..." : "Zatwierdź"}
                        disabled={busy}
                        className="px-6 py-2
                                    bg-[var(--color-si-btn)]
                                    hover:bg-[var(--color-si-btn-hover)] shadow-lg
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FORM_ACTION_CREATE_ORGANIZATION}/>
            </fetcher.Form>
        </Popup>
    );
}
