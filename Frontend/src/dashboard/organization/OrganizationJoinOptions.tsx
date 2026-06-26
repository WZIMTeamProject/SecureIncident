import {useRef, useState} from "react";
import {useFetcher} from "react-router";
import {Popup} from "../../components/Popup.tsx";
import {FORM_ACTION, FormActions, OrganizationForms} from "../forms.ts";

export function OrganizationJoinOptions() {
    const [shownPopup, setShownPopup] = useState<ShownCreateOrganizationPopup>(null);
    const hidePopup = () => setShownPopup(null)

    return (
        <div className="w-full flex gap-3 p-3 justify-end">
            <CreateOrganizationPopup show={shownPopup == "new_organization"} onHide={hidePopup}/>
            <JoinOrganizationPopup show={shownPopup == "join_organization"} onHide={hidePopup}/>

            <button
                onClick={() => setShownPopup("new_organization")}
                className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                Utwórz organizację
            </button>

            <button
                onClick={() => setShownPopup("join_organization")}
                className="px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                Dołącz do organizacji
            </button>
        </div>
    );
}

type ShownCreateOrganizationPopup = "new_organization" | "join_organization" | null;

function CreateOrganizationPopup({show, onHide}: {show: boolean, onHide: () => void}) {
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
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Utwórz nową organizację
                </h1>
                <h3 className="text-lg font-medium text-(--color-si-label)">
                    Wpisz nazwę organizacji:
                </h3>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={organizationName}
                            required={true}
                            type="text"
                            name={OrganizationForms.OrganizationName}
                            placeholder="Nazwa organizacji"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>

                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={organizationDescription}
                            type="text"
                            name={OrganizationForms.Description}
                            placeholder="Opis (opcjonalny)"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
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
                                bg-(--color-si-btn-error)
                                hover:bg-(--color-si-btn-error-hover) shadow-lg
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        Anuluj
                    </button>

                    <input
                        type="submit"
                        value={busy ? "Tworzenie..." : "Zatwierdź"}
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
                    value={FormActions.CreateOrganization}/>
            </fetcher.Form>
        </Popup>
    );
}

function JoinOrganizationPopup({show, onHide}: {show: boolean, onHide: () => void}) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const [pendingHide, setPendingHide] = useState<boolean>(false);

    const tokenNameRef = useRef<HTMLInputElement>(null);

    if (fetcher.state == "idle" && pendingHide) {
        setPendingHide(false);
        onHide();
    }

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST" onSubmit={() => setPendingHide(true)}>
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Podaj token z zaproszenia by dołączyć do organizacji:
                </h1>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={tokenNameRef}
                            required={true}
                            type="text"
                            name={OrganizationForms.InviteToken}
                            placeholder="Podaj token"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        onClick={() => {
                            tokenNameRef.current = null;
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
                        value={busy ? "Dołączanie..." : "Zatwierdź"}
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
                    value={FormActions.JoinOrganization}/>
            </fetcher.Form>
        </Popup>
    );
}
