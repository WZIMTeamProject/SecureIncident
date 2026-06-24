import {
    createContext,
    type LoaderFunction,
    type MiddlewareFunction,
    redirect,
    type RouterContextProvider
} from "react-router";
import Api from "./Api.ts";
import {
    BEARER_AUTH_COOKIE,
    CURRENT_USER_ID_COOKIE,
    CURRENT_USER_IS_DEBUG_COOKIE,
    CURRENT_USER_NAME_COOKIE,
    CURRENT_USER_ORGANIZATION_COOKIE,
} from "./cookies.ts";
import * as React from "react";
import {
    getDummyProjects,
    type Incident,
    type IncidentHistoryEntry,
    type Organization,
    type Project,
} from "./project.ts";
import type {UserProfile} from "./profile.ts";
import {type IncidentLogType, type ProjectScope, ResponseError} from "../api";

export const AuthRouterContext = createContext<AuthState | null>(null);
export const AuthUserContext = React.createContext<AuthState | null>(null);

/** A page of notification feed entries plus the total unpaginated count (for "load more"). */
export interface NotificationsPage {
    items: IncidentHistoryEntry[];
    total: number;
}

export class AuthState {
    name: string;
    id: string;
    organization?: string;
    isDummyUser: boolean;

    constructor(name: string, id: string, isDummyUser: boolean) {
        this.name = name;
        this.id = id;
        this.isDummyUser = isDummyUser;

        if (import.meta.env.DEV && isDummyUser) {
            this.organization = "0000-0000-0000-0001"
        }
    }

    async getOrganization(): Promise<Organization | null> {
        if (import.meta.env.DEV && this.isDummyUser) {
            return {
                id: "0000-0000-0000-0001",
                name: "Moja organizacja",
                description: "Coś tam, coś tam"
            };
        }

        try {
            const organization = await Api.organization.organizationGet();
            return {
                name: organization.name,
                id: organization.id,
                description: organization.description ?? undefined,
            }
        } catch {
            return null;
        }
    }

    async getProjects(scope?: ProjectScope): Promise<Project[]> {
        if (import.meta.env.DEV && this.isDummyUser) {
            const dummyProjects = getDummyProjects();

            if (scope) {
                return dummyProjects.filter((project) => project.scope == scope);
            } else {
                return dummyProjects;
            }
        }

        try {
            const projectList = await Api.projects.projectsGet({scope: scope});
            return projectList.items.map((rawProject) => {
                return {
                    name: rawProject.name,
                    description: rawProject.description ?? undefined,
                    id: rawProject.id,
                    scope: rawProject.scope,
                    organizationId: rawProject.organizationId ?? undefined,
                };
            });
        } catch {
            return [];
        }
    }

    async getReportedIncidents(): Promise<Incident[]> {
        if (import.meta.env.DEV && this.isDummyUser) {
            return [];
        }

        try {
            const incidentList = await Api.incidents.incidentsMyReportedGet();
            return incidentList.items.map((rawIncident) => {
                return {
                    id: rawIncident.id,
                    title: rawIncident.title,
                    primaryAssigneeId: rawIncident.primaryAssigneeId ?? undefined,
                    categoryId: rawIncident.categoryId ?? undefined,
                    reportDate: rawIncident.reportDate,
                    status: rawIncident.status,
                    priority: rawIncident.priority,
                    description: "",
                };
            });
        } catch {
            return [];
        }
    }

    async getAssignedIncidents(): Promise<Incident[]> {
        if (import.meta.env.DEV && this.isDummyUser) {
            return [];
        }

        try {
            const incidentList = await Api.incidents.incidentsMyAssignedGet();
            return incidentList.items.map((rawIncident) => {
                return {
                    id: rawIncident.id,
                    title: rawIncident.title,
                    primaryAssigneeId: rawIncident.primaryAssigneeId ?? undefined,
                    categoryId: rawIncident.categoryId ?? undefined,
                    reportDate: rawIncident.reportDate,
                    status: rawIncident.status,
                    priority: rawIncident.priority,
                };
            });
        } catch {
            return [];
        }
    }

    async getIncidentHistory(projectId?: string, type?: IncidentLogType): Promise<IncidentHistoryEntry[]> {
        if (import.meta.env.DEV && this.isDummyUser) {
            return [];
        }

        try {
            const incidentEntry = await Api.incidents.incidentsHistoryGet({
                projectId: projectId,
                type: type
            });

            return incidentEntry.items.map((rawEntry) => {
                return {
                    id: rawEntry.id,
                    incidentId: rawEntry.incidentId,
                    type: rawEntry.type,
                    actorId: rawEntry.actorId,
                    createdAt: rawEntry.createdAt,
                    newValue: rawEntry.newValue ?? undefined,
                    oldValue: rawEntry.oldValue ?? undefined,
                    comment: rawEntry.comment ?? undefined,
                };
            });
        } catch {
            return [];
        }
    }

    // Errors are intentionally NOT swallowed here (unlike getIncidentHistory): the
    // notification feed has a dedicated error state, so the caller distinguishes a
    // failed load from an empty feed.
    async getNotifications(offset: number = 0, limit: number = 20): Promise<NotificationsPage> {
        if (import.meta.env.DEV && this.isDummyUser) {
            const now = Date.now();
            const items: IncidentHistoryEntry[] = [
                {
                    id: "0000-0000-0000-0001",
                    incidentId: "0000-0000-0000-0001",
                    type: "ASSIGNEE_CHANGED",
                    actorId: "0000-0000-0000-0002",
                    createdAt: new Date(now - 5 * 60 * 1000),
                },
                {
                    id: "0000-0000-0000-0002",
                    incidentId: "0000-0000-0000-0003",
                    type: "COMMENT",
                    actorId: "0000-0000-0000-0004",
                    createdAt: new Date(now - 2 * 60 * 60 * 1000),
                    comment: "Logowanie nie działa po ostatniej aktualizacji.",
                },
            ];
            return {items: items.slice(offset, offset + limit), total: items.length};
        }

        const notifications = await Api.incidents.incidentsNotificationsGet({offset, limit});

        return {
            items: notifications.items.map((rawEntry) => {
                return {
                    id: rawEntry.id,
                    incidentId: rawEntry.incidentId,
                    type: rawEntry.type,
                    actorId: rawEntry.actorId,
                    createdAt: rawEntry.createdAt,
                    newValue: rawEntry.newValue ?? undefined,
                    oldValue: rawEntry.oldValue ?? undefined,
                    comment: rawEntry.comment ?? undefined,
                };
            }),
            total: notifications.total,
        };
    }

    async getProfile(): Promise<UserProfile | null> {
        if (import.meta.env.DEV && this.isDummyUser) {
            return {
                id: this.id,
                username: this.name,
                bio: "Zrobię to jutro",
                profilePictureURL: "https://cdn.7tv.app/emote/01HBVADK180003KFD14YHJ4PRZ/4x.png"
            };
        }

        try {
            const profile = await Api.profiles.profilesMeGet();
            return {
                id: profile.id,
                username: profile.username,
                bio: profile.bio ?? undefined,
                profilePictureURL: profile.profilePictureUrl ?? undefined,
            };
        } catch {
            return null;
        }
    }
}

export interface RegistrationResult {
    success: boolean;
    id?: string;
    errorCause?: "username_or_email_taken" | "username_too_short" | "unknown";
}

/**
 * Gets the authentication state from the browser cookies.
 *
 * @param forceValidate If set to `false`, the function will blindly trust the data stored in cookies and not validate it with the server.
 * @returns The auth state of the current user, or `null` if not logged in.
 */
export async function getAuthState(forceValidate: boolean = true): Promise<AuthState | null> {
    const [idCookie, usernameCookie, organizationCookie] = await Promise.all([
        cookieStore.get(CURRENT_USER_ID_COOKIE),
        cookieStore.get(CURRENT_USER_NAME_COOKIE),
        cookieStore.get(CURRENT_USER_ORGANIZATION_COOKIE)
    ]);

    const [id, username, organizationId] = [
        idCookie?.value,
        usernameCookie?.value,
        organizationCookie?.value
    ];

    if (import.meta.env.DEV) {
        const isDebugCookie = await cookieStore.get(CURRENT_USER_IS_DEBUG_COOKIE);

        if (id && username && isDebugCookie && isDebugCookie.value == "1") {
            // Simulate a 100ms delay each time auth state is requested while using dummy data
            const simulatedDelay = 100;
            await new Promise((resolve) => setTimeout(resolve, simulatedDelay));

            return new AuthState(username, id, true);
        }
    }

    if (forceValidate || !id || !username) {
        const currentUser = await Api.auth.authMeGet().catch(() => null);

        if (currentUser) {
            const {username, id, organizationId} = currentUser;

            await cookieStore.set(CURRENT_USER_ID_COOKIE, id);
            await cookieStore.set(CURRENT_USER_NAME_COOKIE, username);

            if (organizationId) {
                await cookieStore.set(CURRENT_USER_ORGANIZATION_COOKIE, organizationId);
            } else {
                await cookieStore.delete(CURRENT_USER_ORGANIZATION_COOKIE);
            }

            if (import.meta.env.DEV) {
                const isDebugCookie = await cookieStore.get(CURRENT_USER_IS_DEBUG_COOKIE);

                if (isDebugCookie != null) {
                    console.error(`User is logged with a non-debug account, but the ${CURRENT_USER_IS_DEBUG_COOKIE} cookie is set.`);
                }
            }

            const createdAuth = new AuthState(username, id, false);
            createdAuth.organization = organizationId ?? undefined;

            return createdAuth;
        } else {
            await cookieStore.delete(BEARER_AUTH_COOKIE); // Remove the remaining login cookie, cause it means it's invalid
            return null;
        }
    }

    const createdAuth = new AuthState(username, id, false);
    createdAuth.organization = organizationId ?? undefined;

    return createdAuth;
}

/**
 * When used as router middleware, redirects the user to the login page if they are not logged in.
 */
export const authGuardMiddleware: MiddlewareFunction = async ({context}, next) => {
    const currentAuthState = context.get(AuthRouterContext);

    if (!currentAuthState) {
        throw redirect("/login");
    }

    return await next();
}

/**
 * Utility loader that works similarly to `authGuardMiddleware`, but allows getting the actual AuthState with `useLoaderData()`.
 */
export const authUserLoader: LoaderFunction = async ({context}) => {
    const middlewareContext = (context as Readonly<RouterContextProvider>);

    const currentAuthState = middlewareContext.get(AuthRouterContext);

    if (!currentAuthState) {
        throw redirect("/login");
    }

    return currentAuthState;
};

/**
 * Attempts to log in a user with the given credentials.
 *
 * @returns Whether the user was successfully logged in.
 */
export async function attemptLogin(name: string, password: string, remember_user: boolean): Promise<boolean> {
    const currentUser = await getAuthState();

    if (currentUser != null) {
        // TODO: should this log you out and try to relog you with new credentials?
        console.error("Login was requested, but user is already logged in.");
        return true;
    }

    // When running in debug, allow logging in with a debug username `DEBUG@<USERNAME>`,
    // where <USERNAME> can be any value. Useful for testing ui with names of different length.
    if (import.meta.env.DEV) {
        const nameParts = name.split("@");

        if (nameParts.length >= 2) {
            const [prefix, customDebugUsername] = nameParts;

            if (prefix == "DEBUG" && customDebugUsername.length > 0 && password.length > 0) {
                await Promise.all([
                    cookieStore.set(CURRENT_USER_ID_COOKIE, "0000-0000-0000-0000"),
                    cookieStore.set(CURRENT_USER_NAME_COOKIE, customDebugUsername),
                    cookieStore.set(CURRENT_USER_IS_DEBUG_COOKIE, "1"),
                    cookieStore.delete(CURRENT_USER_ORGANIZATION_COOKIE)
                ]);

                return true;
            }
        }
    }

    const loggedUser = await Api.auth.authLoginPost({
        loginRequest: {
            username: name,
            password: password,
            rememberUser: remember_user,
        }
    }).catch(() => null);

    if (loggedUser != null) {
        const token: string = loggedUser.accessToken;
        const tokenLifetime: number = 1000 * 60 * 60 * 24 * 7; // 1 week

        await cookieStore.set({
            name: BEARER_AUTH_COOKIE,
            value: token,
            sameSite: "strict",
            expires: Date.now() + tokenLifetime,
        });
    }

    return loggedUser != null;
}

/**
 * Logs out the current user. Safe to call even when no user is logged in.
 */
export async function attemptLogout() {
    // Always delete everything on logout, even if something fails, no login data should remain
    await Api.auth.authLogoutPost().catch(() => null);
    await cookieStore.delete(BEARER_AUTH_COOKIE).catch(() => null);
    await cookieStore.delete(CURRENT_USER_ID_COOKIE).catch(() => null);
    await cookieStore.delete(CURRENT_USER_NAME_COOKIE).catch(() => null);
    await cookieStore.delete(CURRENT_USER_IS_DEBUG_COOKIE).catch(() => null);
    await cookieStore.delete(CURRENT_USER_ORGANIZATION_COOKIE).catch(() => null);
}

export async function attemptRegistration(
    firstName: string,
    lastName: string,
    username: string,
    email: string,
    password: string
): Promise<RegistrationResult> {
    try {
        const response = await Api.auth.authRegisterPost({
            registerRequest: {
                firstName: firstName,
                lastName: lastName,
                username: username,
                email: email,
                password: password,
            }
        });

        return {success: true, id: response.id}
    } catch (ex) {
        let status = 0;

        if (ex instanceof ResponseError) {
            status = ex.response.status;
        }

        switch (status) {
            case 409:
                return {
                    success: false,
                    errorCause: "username_or_email_taken",
                };
            case 422:
                // Why is this undocumented in the api?
                // This also happens when the password does not meet the requirements...
                return {
                    success: false,
                    errorCause: "username_too_short",
                };
            default:
                return {
                    success: false,
                    errorCause: "unknown",
                };
        }
    }
}
