import type {Project} from "../../data/project.ts";
import {useRef, useState} from "react";
import * as React from "react";
import type {ProjectInfo} from "../SIProject.tsx";
import type {IncidentSummary} from "../../api";
import {Link, useFetcher} from "react-router";
import {FORM_ACTION, FormActions, ProjectForms} from "../forms.ts";
import {Popup} from "../../components/Popup.tsx";

export function IncidentList({show, project, projectInfo}: { show: boolean, project?: Project, projectInfo?: ProjectInfo }) {
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const hidePopup = () => setShowPopup(false);

    const disableButtons: boolean = project === undefined;
    const incidents = projectInfo?.incidents;

    const canCreateIncidents = projectInfo?.myRole?.permissions.canWriteTickets ?? false;

    return (
        <div hidden={!show}>
            {
                project && canCreateIncidents
                    ? <NewIncidentPopup show={showPopup} onHide={hidePopup} project={project}/>
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
                    onClick={() => setShowPopup(true)}
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
