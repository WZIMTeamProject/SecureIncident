import {useParams} from "react-router";
import {useEffect, useMemo, useState} from "react";
import type {Incident} from "../data/project.ts";
import Api from "../data/Api.ts";
import type {IncidentLogEntry} from "../api";
import * as React from "react";

export function SIIncident() {
    const urlParams = useParams();

    const [incident, setIncident] = useState<Incident | null>();

    useEffect(() => {
        const incidentId = urlParams["incidentId"];

        if (incidentId) {
            Api.incidents.incidentsIncidentIdGet({
                incidentId: incidentId,
            }).then(
                (incidentResponse) => {
                    setIncident({
                        title: incidentResponse.title,
                        id: incidentResponse.id,
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
    }, [urlParams]);

    if (incident === undefined) {
        return <LoadingMessage/>;
    }

    return (
        <div>
            {incident === null ? "ERROR" : <IncidentView incident={incident}/>}
        </div>
    );
}

function LoadingMessage() {
    return <h1>Wczytywanie...</h1>;
}

function IncidentView({incident}: { incident: Incident }) {
    const [logs, setLogs] = useState<IncidentLogEntry[] | undefined>(undefined);

    useEffect(() => {
        Api.incidents.incidentsIncidentIdLogsGet({
            incidentId: incident.id,
            limit: undefined
        }).then(
            (incidentLogs) => setLogs(incidentLogs.items),
            () => setLogs([]),
        );
    }, [incident, logs]);

    return (
        <div className={"flex flex-col gap-3"}>
            <div className="bg-(--color-si-card-bg) border-5 border-(--color-si-card-border) w-fit
                    rounded-2xl shadow-lg p-4 transition-colors duration-300">

                <h1 className="text-2xl font-bold text-(--color-si-label)">
                    {incident.title}
                </h1>
                <h3 className="text-md italic text-(--color-si-input-text)">
                    {incident.id}
                </h3>

                <hr className="my-2"/>

                <p>
                    <span className="text-(--color-si-label)">Przypisani: </span>
                    <span className="text-(--color-si-input-text)">
                        {incident.primaryAssigneeId ?? "- Brak -"}
                    </span>
                </p>
                <p>
                    <span className="text-(--color-si-label)">Priorytet: </span>
                    <span className="text-(--color-si-input-text)">
                        {incident.priority}
                    </span>
                </p>
                <p>
                    <span className="text-(--color-si-label)">Status: </span>
                    <span className="text-(--color-si-input-text)">
                        {incident.status}
                    </span>
                </p>
                <p>
                    <span className="text-(--color-si-label)">Zgłoszono: </span>
                    <span className="text-(--color-si-input-text)">
                        {incident.reportDate.toLocaleString()}
                    </span>
                </p>
            </div>

            <div className="bg-(--color-si-card-bg) border border-(--color-si-card-border)
                    rounded-2xl shadow-lg p-4 transition-colors duration-300">
                <span className="text-(--color-si-input-text) italic">Opis:</span><br/>
                <span className="text-(--color-si-label)">
                    {incident.description}
                </span>
            </div>

            <LogHistory logs={logs} />
        </div>
    );
}

function LogHistory({logs}: { logs?: IncidentLogEntry[] }) {
    const logNodes = useMemo(() => {
        return logs?.map(log => <LogEntry log={log}/>);
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

function LogEntry({log} : {log: IncidentLogEntry}){
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