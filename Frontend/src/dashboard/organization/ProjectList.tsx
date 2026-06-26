import {Link, useFetcher} from "react-router";
import {useContext, useDeferredValue, useEffect, useRef, useState} from "react";
import {AuthUserContext} from "../../data/auth.ts";
import type {Organization, Project} from "../../data/project.ts";
import {Popup} from "../../components/Popup.tsx";
import {FORM_ACTION, FormActions, OrganizationForms} from "../forms.ts";
import {IconCheck, IconClipboard} from "../../components/icons.tsx";

type ShownOrganizationPopup = "new_project" | "invite_user" | "delete_organization" | null;

export function ProjectList({organization}: { organization: Organization }) {
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
                <h1 className="text-2xl font-bold text-(--color-si-label)">{organization.name}</h1>
                <p className="text-md text-(--color-si-input-text) italic font-normal">{organization.description ?? "Brak opisu"}</p>
            </div>

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll text-(--color-si-input-text)">
                {
                    projects?.map((project) => {
                        return <p>
                            <Link to={`/dashboard/project/${project.id}`} className={"hover:underline"}>
                                {project.name} - {project.id}
                            </Link>
                        </p>;
                    }) ?? <h1>Ładowanie...</h1>
                }
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button
                    onClick={() => setShownPopup("new_project")}
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj nowy projekt
                </button>

                <button
                    onClick={() => setShownPopup("invite_user")}
                    className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj użytkownika do organizacji
                </button>
            </div>

            <div className="w-full flex px-3 justify-end">
                <button
                    onClick={() => setShownPopup("delete_organization")}
                    className="px-6 py-2
                        bg-(--color-si-btn-error)
                        hover:bg-(--color-si-btn-error-hover) shadow-lg
                        text-white text-md font-semibold underline rounded-lg cursor-pointer transition-colors duration-200">
                    Usuń organizację
                </button>
            </div>
        </div>
    );
}

function NewProjectPopup({show, onHide}: { show: boolean, onHide: () => void }) {
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
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Nowy Projekt
                </h1>
                <h3 className="text-lg font-medium text-(--color-si-input-text)">
                    Podaj dane nowego projektu:
                </h3>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={projectNameRef}
                            type="text"
                            required={true}
                            name={OrganizationForms.ProjectName}
                            placeholder="Nazwa"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>

                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={projectDescriptionRef}
                            type="text"
                            name={OrganizationForms.Description}
                            placeholder="Opis (opcjonalny)"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
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
                            bg-(--color-si-btn-error)
                            hover:bg-(--color-si-btn-error-hover) shadow-lg
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Zapisywanie..." : "Zapisz"}
                        disabled={busy}
                        className="px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FormActions.NewProject}/>
            </fetcher.Form>
        </Popup>
    );
}

function AddToOrganizationPopup({show, onHide}: {show: boolean, onHide: () => void}) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [copiedToken, setCopiedToken] = useState<boolean>(false);
    const [copiedLink, setCopiedLink] = useState<boolean>(false);

    const inviteCountRef = useRef<HTMLInputElement>(null);

    const inviteToken = fetcher.data?.ok ? fetcher.data.token : null;
    const inviteLink = fetcher.data?.ok ? fetcher.data.inviteUrl : null;

    const previousShowState = useDeferredValue(show);

    if (fetcher.data && previousShowState && !show) {
        fetcher.reset();
    }

    if (!show && (copiedToken || copiedLink)) {
        setCopiedLink(false);
        setCopiedToken(false);
    }

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => fetcher.reset()}>
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Dodaj do organizacji
                </h1>
                <h3 className="text-lg font-medium text-(--color-si-input-text)">
                    Wygeneruj token którego inni użytkownicy mogą użyć do dołączenia.
                </h3>

                <div className="flex gap-1.5 my-3 justify-center items-center">
                    <span className="text-(--color-si-input-icon)">
                        Liczba użytkowników:
                    </span>

                    <div className="flex items-center gap-3
                            border border-(--color-si-input-border)
                            rounded-lg px-3 py-2.5
                            bg-(--color-si-input-bg) transition-colors">

                        <input
                            ref={inviteCountRef}
                            type="number"
                            min={1}
                            max={20}
                            defaultValue={1}
                            name={OrganizationForms.InviteCount}
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div hidden={!inviteToken} className="flex flex-col gap-1.5">
                    <span className="text-sm font-medium text-(--color-si-label)">Token do dołączenia:</span>
                    <div
                        className="flex items-center gap-3 mb-3
                            border border-(--color-si-input-border)
                            rounded-lg px-2.5 py-2
                            bg-(--color-si-input-bg) transition-colors">

                        <button
                            form=""
                            title="Skopiuj token"
                            onClick={() => {
                                navigator.clipboard.writeText(inviteToken)
                                    .then(() => {
                                        setCopiedToken(true);
                                        setCopiedLink(false);
                                    });
                            }}
                            className="p-2
                                bg-(--color-si-btn)
                                hover:bg-(--color-si-btn-hover)
                                disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                            {copiedToken ? <IconCheck/> : <IconClipboard/>}
                        </button>
                        <span className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)">
                            {inviteToken}
                        </span>
                    </div>
                </div>

                <div hidden={!inviteLink} className="flex flex-col gap-1.5">
                    <span className="text-sm font-medium text-(--color-si-label)">Link do dołączenia:</span>
                    <div
                        className="flex items-center gap-3 mb-3
                            border border-(--color-si-input-border)
                            rounded-lg px-2.5 py-2
                            bg-(--color-si-input-bg) transition-colors">

                        <button
                            form=""
                            title="Skopiuj link"
                            onClick={() => {
                                navigator.clipboard.writeText(inviteLink)
                                    .then(() => {
                                        setCopiedToken(false);
                                        setCopiedLink(true);
                                    });
                            }}
                            className="p-2
                                bg-(--color-si-btn)
                                hover:bg-(--color-si-btn-hover)
                                disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                            {copiedLink ? <IconCheck/> : <IconClipboard/>}
                        </button>

                        <span className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)">
                            {inviteLink}
                        </span>
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        onClick={() => {
                            inviteCountRef.current = null;
                            onHide();
                        }}
                        className="px-6 py-2
                            bg-(--color-si-btn-error)
                            hover:bg-(--color-si-btn-error-hover) shadow-lg
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Zamknij
                    </button>

                    <input
                        type="submit"
                        onSubmit={() => {
                            setCopiedToken(false);
                            setCopiedLink(false);
                        }}
                        value={busy ? "Generowanie..." : "Wygeneruj"}
                        disabled={busy}
                        className="px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FormActions.InviteUser}/>
            </fetcher.Form>

        </Popup>
    );
}

function DeleteOrganizationPopup({show, onHide}: {show: boolean, onHide: () => void}) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="DELETE">
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    USUWANIE ORGANIZACJI
                </h1>

                <h3 className="text-lg font-medium mt-2 mb-4 text-(--color-si-input-text)">
                    Czy na pewno chcesz usunąć organizację?
                    Usunie ją to bezpowrotnie z Twojego dashboardu razem z projektami!
                </h3>

                <div className="flex items-center justify-between">
                    <button
                        onClick={onHide}
                        className="px-6 py-2
                                bg-(--color-si-btn)
                                hover:bg-(--color-si-btn-hover) shadow-lg
                                text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        NIE, ANULUJ
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Usuwanie..." : "Tak, usuń"}
                        disabled={busy}
                        className="px-6 py-2
                                    bg-(--color-si-btn-error)
                                    hover:bg-(--color-si-btn-error-hover) shadow-lg
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                    />
                </div>

                <input
                    name={FORM_ACTION}
                    type="hidden"
                    value={FormActions.DeleteOrganization}/>
            </fetcher.Form>
        </Popup>
    );
}

