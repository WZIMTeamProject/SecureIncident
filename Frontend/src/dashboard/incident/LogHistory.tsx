import {useMemo, useState} from "react";
import type {IncidentLogEntry} from "../../api";
import * as React from "react";
import {LoadingMessage} from "../../components/LoadingMessage.tsx";

export function LogHistory({logs}: { logs?: IncidentLogEntry[] }) {
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
