import {useEffect, useState} from "react";
import {Link, useLoaderData} from "react-router";
import type {AuthState} from "../data/auth.ts";
import type {IncidentHistoryEntry} from "../data/project.ts";
import type {IncidentLogType} from "../api";
import {IconComment, IconUser} from "../components/icons.tsx";
import {Background} from "../components/Background.tsx";

const NOTIFICATION_LABELS: Record<IncidentLogType, string> = {
    ASSIGNEE_CHANGED: "Przydzielono Cię do incydentu",
    COMMENT: "Nowy komentarz",
    STATUS_CHANGED: "Zmiana statusu",
    CLOSED: "Incydent zamknięty",
    PRIORITY_CHANGED: "Zmiana priorytetu",
    CATEGORY_CHANGED: "Zmiana kategorii",
    HELPER_ADDED: "Dodano pomocnika",
    HELPER_REMOVED: "Usunięto pomocnika",
    CREATED: "Utworzono incydent",
};

function labelForType(type: IncidentLogType): string {
    return NOTIFICATION_LABELS[type] ?? "Powiadomienie";
}

function formatRelativeTime(date: Date): string {
    const diffSeconds = Math.round((Date.now() - date.getTime()) / 1000);

    if (diffSeconds < 60) {
        return "przed chwilą";
    }

    const diffMinutes = Math.round(diffSeconds / 60);
    if (diffMinutes < 60) {
        return `${diffMinutes} min temu`;
    }

    const diffHours = Math.round(diffMinutes / 60);
    if (diffHours < 24) {
        return `${diffHours} godz. temu`;
    }

    const diffDays = Math.round(diffHours / 24);
    return `${diffDays} dni temu`;
}

const PAGE_SIZE = 20;

export function SINotificationPage() {
    const auth = useLoaderData<AuthState>();

    const [notifications, setNotifications] = useState<IncidentHistoryEntry[] | null | undefined>(undefined);
    const [total, setTotal] = useState(0);
    const [loadingMore, setLoadingMore] = useState(false);

    useEffect(() => {
        let ignore = false;

        auth.getNotifications(0, PAGE_SIZE).then(
            (page) => {
                if (!ignore) {
                    setNotifications(page.items);
                    setTotal(page.total);
                }
            },
            () => {
                if (!ignore) {
                    setNotifications(null);
                }
            }
        );

        return () => {
            ignore = true;
        };
    }, [auth]);

    const loaded = notifications ?? [];
    const hasMore = notifications != null && loaded.length < total;

    const loadMore = () => {
        if (loadingMore || notifications == null) {
            return;
        }

        setLoadingMore(true);
        auth.getNotifications(loaded.length, PAGE_SIZE).then(
            (page) => {
                setNotifications((prev) => [...(prev ?? []), ...page.items]);
                setTotal(page.total);
                setLoadingMore(false);
            },
            () => {
                // Keep the already-loaded items; a failed "load more" just stops the spinner.
                setLoadingMore(false);
            }
        );
    };

    return (
        <Background>
            <div className="w-full max-w-2xl flex flex-col gap-4">
                <h1 className="text-3xl font-bold text-(--color-si-label)">
                    Powiadomienia
                </h1>

                <NotificationFeed notifications={notifications}/>

                {hasMore && (
                    <button
                        type="button"
                        onClick={loadMore}
                        disabled={loadingMore}
                        className="min-h-11 px-6 py-2 self-center bg-(--color-si-btn) hover:bg-(--color-si-btn-hover)
                            disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                        {loadingMore ? "Wczytywanie..." : "Pokaż więcej"}
                    </button>
                )}

                <Link
                    to="/account"
                    className="min-h-11 flex items-center text-sm underline text-(--color-si-link) hover:opacity-75">
                    Wróć
                </Link>
            </div>
        </Background>
    );
}

interface NotificationFeedProps {
    notifications: IncidentHistoryEntry[] | null | undefined;
}

function NotificationFeed({notifications}: NotificationFeedProps) {
    if (notifications === undefined) {
        return (
            <div className="border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">
                <h1 className="text-(--color-si-label)">Wczytywanie...</h1>
            </div>
        );
    }

    if (notifications === null) {
        return (
            <div
                role="alert"
                className="border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">
                <p className="text-red-500 dark:text-red-400 text-sm">
                    Nie udało się wczytać powiadomień. Spróbuj ponownie później.
                </p>
            </div>
        );
    }

    if (notifications.length === 0) {
        return (
            <div className="border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">
                <p className="text-(--color-si-input-text) italic">Brak powiadomień</p>
            </div>
        );
    }

    return (
        <div className="max-h-96 overflow-y-auto
                border-5 border-(--color-si-card-border)
                rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">
            {notifications.map((notification) => (
                <NotificationItem key={notification.id} notification={notification}/>
            ))}
        </div>
    );
}

interface NotificationItemProps {
    notification: IncidentHistoryEntry;
}

function NotificationItem({notification}: NotificationItemProps) {
    return (
        <Link
            to={`/dashboard/incident/${notification.incidentId}`}
            className="min-h-11 flex gap-3 items-start py-3
                border-b border-(--color-si-input-border)
                hover:opacity-75 transition-opacity">
            <span aria-hidden="true" className="text-(--color-si-input-icon) mt-0.5">
                {notification.type === "COMMENT" ? <IconComment/> : <IconUser/>}
            </span>

            <span className="flex-1 flex flex-col gap-0.5">
                <span className="text-sm font-semibold text-(--color-si-label)">
                    {labelForType(notification.type)}
                </span>

                {notification.type === "COMMENT" && notification.comment && (
                    <span className="text-sm text-(--color-si-input-text)">
                        {notification.comment}
                    </span>
                )}

                <span className="text-xs text-(--color-si-input-text)">
                    przez {notification.actorId} · {formatRelativeTime(notification.createdAt)}
                </span>

                <span className="text-xs text-(--color-si-link) underline">
                    Zobacz incydent
                </span>
            </span>
        </Link>
    );
}
