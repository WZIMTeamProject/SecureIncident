import {useFetcher, useParams} from "react-router";
import * as React from "react";
import {useEffect, useMemo, useRef, useState} from "react";
import type {Incident} from "../data/project.ts";
import Api from "../data/Api.ts";
import type {IncidentLogEntry, ProjectMemberResponse} from "../api";
import {Popup} from "../components/Popup.tsx";
import {FORM_ACTION, FORM_ACTION_INVITE_USER, FORM_INVITE_NAME} from "./forms.ts";

export function SIIncident() {
    const urlParams = useParams();
    const [incident, setIncident] = useState<Incident | null>();

    const incidentId = urlParams["incidentId"];

    if (incident && incident.id !== incidentId) {
        if (incidentId) {
            setIncident(undefined);
        } else {
            setIncident(null);
        }
    }

    useEffect(() => {
        if (incidentId) {
            Api.incidents.incidentsIncidentIdGet({
                incidentId: incidentId,
            }).then(
                (incidentResponse) => {
                    setIncident({
                        title: incidentResponse.title,
                        id: incidentResponse.id,
                        projectId: incidentResponse.projectId,
                        primaryAssigneeId: incidentResponse.primaryAssigneeId ?? undefined,
                        categoryId: incidentResponse.categoryId ?? undefined,
                        reportDate: incidentResponse.reportDate,
                        priority: incidentResponse.priority,
                        status: incidentResponse.status,
                        description: incidentResponse.description,
                    })
                },
                () => setIncident(null),
            );
        }
    }, [incidentId]);

    return (
        <div>
            {incident === null ? "ERROR" : <IncidentView incident={incident}/>}
        </div>
    );
}

function LoadingMessage() {
    return <h1>Wczytywanie...</h1>;
}

type IncidentPopupType = "add_to_incident" | null;

function IncidentView({incident}: { incident?: Incident }) {
    const [logs, setLogs] = useState<IncidentLogEntry[] | undefined>(undefined);
    const [shownPopup, setShownPopup] = useState<IncidentPopupType>(null);
    const hidePopup = () => setShownPopup(null);

    if (logs && incident === undefined) {
        setLogs(undefined);
    }

    useEffect(() => {
        if (incident) {
            Api.incidents.incidentsIncidentIdLogsGet({
                incidentId: incident.id,
                limit: undefined
            }).then(
                (incidentLogs) => setLogs(incidentLogs.items),
                () => setLogs([]),
            );
        }
    }, [incident]);

    const disableButtons: boolean = incident === undefined;

    return (
        <div className={"flex flex-col gap-3"}>
            {
                incident
                    ? <AddToIncidentPopup
                        incident={incident}
                        show={shownPopup == "add_to_incident"}
                        onHide={hidePopup}/>
                    : undefined
            }

            <div className={"flex gap-3"}>
                <div className="bg-(--color-si-card-bg) border-5 border-(--color-si-card-border) w-fit
                    rounded-2xl shadow-lg p-4 transition-colors duration-300">

                    <h1 className="text-2xl font-bold text-(--color-si-label)">
                        {incident?.title ?? "Wczytywanie..."}
                    </h1>
                    <h3 className="text-md italic text-(--color-si-input-text)">
                        {incident?.id ?? "-"}
                    </h3>

                    <hr className="my-2"/>

                    <p>
                        <span className="text-(--color-si-label)">Przypisani: </span>
                        <span className="text-(--color-si-input-text)">
                        {incident ? (incident.primaryAssigneeId ?? "- Brak -") : "..."}
                    </span>
                    </p>
                    <p>
                        <span className="text-(--color-si-label)">Priorytet: </span>
                        <span className="text-(--color-si-input-text)">
                        {incident?.priority ?? "..."}
                    </span>
                    </p>
                    <p>
                        <span className="text-(--color-si-label)">Status: </span>
                        <span className="text-(--color-si-input-text)">
                        {incident?.status ?? "..."}
                    </span>
                    </p>
                    <p>
                        <span className="text-(--color-si-label)">Zgłoszono: </span>
                        <span className="text-(--color-si-input-text)">
                            {incident?.reportDate.toLocaleString() ?? "..."}
                        </span>
                    </p>
                </div>

                <div className="flex-1"></div>

                <div className="flex flex-col justify-center gap-3">
                    <button
                        disabled={disableButtons}
                        className={`px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg rounded-lg
                            text-white text-md font-semibold cursor-pointer transition-colors duration-200`}>
                        Zmień status
                    </button>

                    <button
                        disabled={disableButtons}
                        onClick={() => setShownPopup("add_to_incident")}
                        className={`px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg rounded-lg
                            text-white text-md font-semibold cursor-pointer transition-colors duration-200`}>
                        Dodaj użytkownika
                    </button>

                    <button
                        disabled={disableButtons}
                        className={`px-6 py-2
                            bg-(--color-si-btn)
                            hover:bg-(--color-si-btn-hover) shadow-lg rounded-lg
                            text-white text-md font-semibold cursor-pointer transition-colors duration-200`}>
                        Dodaj komentarz
                    </button>
                </div>
            </div>

            <div className="bg-(--color-si-card-bg) border border-(--color-si-card-border)
                    rounded-2xl shadow-lg p-4 transition-colors duration-300">
                <span className="text-(--color-si-input-text) italic">Opis:</span><br/>
                <span className="text-(--color-si-label)">
                    {incident?.description ?? "..."}
                </span>
            </div>

            <LogHistory logs={logs}/>
        </div>
    );
}

function LogHistory({logs}: { logs?: IncidentLogEntry[] }) {
    const logNodes = useMemo(() => {
        return logs?.map(log => <LogEntry key={log.id} log={log}/>);
    }, [logs]);

    const [isShown, setIsShown] = useState(false);
    const toggleHistory = () => setIsShown(s => !s);

    return (
        <div>
            <button
                onClick={toggleHistory}
                className={`px-6 py-2
                        bg-(--color-si-btn)
                        hover:bg-(--color-si-btn-hover) shadow-lg
                        rounded-t-lg ${isShown ? "" : "rounded-b-lg"}
                        text-white text-md font-semibold cursor-pointer transition-colors duration-200`}>

                {isShown ? "Ukryj historię" : "Pokaż historię"}
            </button>
            <div
                className="border-5 border-(--color-si-card-border) bg-(--color-si-input-bg)
                    rounded-2xl rounded-tl-none shadow-lg p-4 transition-colors duration-300 overflow-y-scroll"
                hidden={!isShown}>

                {logNodes === undefined ? <LoadingMessage/> : logNodes}
            </div>
        </div>
    );
}

function LogEntry({log}: { log: IncidentLogEntry }) {
    let rowContents: string = "";
    const logTime = log.createdAt.toLocaleString();

    switch (log.type) {
        case "COMMENT":
            rowContents = `[${logTime}] Dodano komentarz: ${log.comment?.substring(0, 20)}`;
            break;
        case "STATUS_CHANGED":
            rowContents = `[${logTime}] Zmieniono status: ${log.oldValue} -> ${log.newValue}`;
            break;
        case "ASSIGNEE_CHANGED":
            rowContents = `[${logTime}] Zmieniono przypisaną osobę: ${log.oldValue} -> ${log.newValue}`;
            break;
        case "HELPER_ADDED":
            rowContents = `[${logTime}] Dodano pomocnika: ${log.actorId}`;
            break;
        case "HELPER_REMOVED":
            rowContents = `[${logTime}] Usunięto pomocnika: ${log.actorId}`;
            break;
        case "PRIORITY_CHANGED":
            rowContents = `[${logTime}] Zmieniono priorytet: ${log.oldValue} -> ${log.newValue}`;
            break;
        case "CATEGORY_CHANGED":
            rowContents = `[${logTime}] Zmieniono kategorię: ${log.oldValue} -> ${log.newValue}`;
            break;
        case "CREATED":
            rowContents = `[${logTime}] Otwarto zgłoszenie`;
            break;
        case "CLOSED":
            rowContents = `[${logTime}] Zamknięto zgłoszenie`;
            break;
        default:
            console.error(`Unknown incident log entry "${log.type}"`);
            return <></>;
    }

    return <h1 className={"text-(--color-si-input-text) font-normal"}>
        {rowContents}
    </h1>;
}

function AddToIncidentPopup({incident, show, onHide}: { incident: Incident, show: boolean, onHide: () => void }) {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";

    const usernameRef = useRef<HTMLInputElement>(null);

    const [projectMembers, setProjectMembers] = useState<ProjectMemberResponse[]>([]);

    useEffect(() => {
        const projectId = incident.projectId;
        if (projectId) {
            Api.projects.projectsProjectIdMembersGet({
                projectId: projectId,
            }).then(
                (members) => setProjectMembers(members.members),
                () => setProjectMembers([])
            );
        }
    }, [incident]);

    const projectMemberEntries = useMemo(() => {
        return projectMembers.map((member) => (
            <div key={member.userId} className={"w-full px-3 py-2.5"}>
                <p>{member.username} - {member.roleName}</p>
                <hr/>
            </div>
        ));
    }, [projectMembers]);

    return (
        <Popup show={show} className={"w-full max-w-xl"}>
            <fetcher.Form method="POST">
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Przypisz pomocnika
                </h1>
                <h3 className="text-lg font-medium text-(--color-si-input-text)">
                    Podaj nazwę użytkownika do dodania jako pomocnika tego incydentu:
                </h3>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                        <input
                            ref={usernameRef}
                            id={FORM_INVITE_NAME}
                            type="text"
                            required={true}
                            name={FORM_INVITE_NAME}
                            placeholder="Nazwa użytkownika"
                            className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                        />
                    </div>
                </div>

                <div className="flex flex-col gap-1.5 my-3">
                    <div className="flex items-center gap-3 h-32
                                border border-(--color-si-input-border)
                                rounded-lg
                                bg-(--color-si-input-bg) transition-colors overflow-y-scroll">
                        {projectMemberEntries}
                    </div>
                </div>

                <div className="flex items-center justify-between">
                    <button
                        onClick={() => {
                            usernameRef.current = null;
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
                    value={FORM_ACTION_INVITE_USER}/>
            </fetcher.Form>
        </Popup>
    );
}
