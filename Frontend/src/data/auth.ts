import {createContext, type MiddlewareFunction, redirect} from "react-router";
import Api from "./Api.ts";
import {CURRENT_USER_ID_COOKIE, CURRENT_USER_IS_DEBUG_COOKIE, CURRENT_USER_NAME_COOKIE} from "./cookies.ts";

export const AuthContext = createContext<AuthState | null>(null);

export class AuthState {
    name: string;
    id: string;
    isDummyUser: boolean;

    constructor(name: string, id: string, isDummyUser: boolean) {
        this.name = name;
        this.id = id;
        this.isDummyUser = isDummyUser;
    }
}

/**
 * Gets the authentication state from the browser cookies.
 *
 * @param forceValidate If set to `false`, the function will blindly trust the data stored in cookies and not validate it with the server.
 * @returns The auth state of the current user, or `null` if not logged in.
 */
export async function getAuthState(forceValidate: boolean = true): Promise<AuthState | null> {
    const [idCookie, usernameCookie] = await Promise.all([
        cookieStore.get(CURRENT_USER_ID_COOKIE),
        cookieStore.get(CURRENT_USER_NAME_COOKIE)
    ]);

    const [id, username] = [
        idCookie?.value,
        usernameCookie?.value
    ];

    if (import.meta.env.DEV) {
        const isDebugCookie = await cookieStore.get(CURRENT_USER_IS_DEBUG_COOKIE);

        if (id && username && isDebugCookie && isDebugCookie.value == "1") {
            return new AuthState(username, id, true);
        }
    }

    if (forceValidate || !id || !username) {
        const currentUser = await Api.auth.authMeGet().catch(() => null);

        if (currentUser) {
            const {username, id} = currentUser;

            await cookieStore.set(CURRENT_USER_ID_COOKIE, id);
            await cookieStore.set(CURRENT_USER_NAME_COOKIE, username);

            if (import.meta.env.DEV) {
                const isDebugCookie = await cookieStore.get(CURRENT_USER_IS_DEBUG_COOKIE);

                if (isDebugCookie != null) {
                    console.error(`User is logged with a non-debug account, but the ${CURRENT_USER_IS_DEBUG_COOKIE} cookie is set.`);
                }
            }

            return new AuthState(username, id, false);
        } else {
            return null;
        }
    }

    return new AuthState(username, id, false);
}

/**
 * When used as router middleware, redirects the user to the login page if they are not logged in.
 */
export const authGuardMiddleware: MiddlewareFunction = async ({context}, next) => {
    const currentAuthState = await getAuthState();

    if (currentAuthState) {
        context.set(AuthContext, currentAuthState);
    } else {
        throw redirect("/login");
    }

    return await next();
}

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
                    cookieStore.set(CURRENT_USER_IS_DEBUG_COOKIE, "1")
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

    return loggedUser != null;
}

/**
 * Logs out the current user. Safe to call even when no user is logged in.
 */
export async function attemptLogout() {
    // Always delete everything on logout, even if something fails, no login data should remain
    await Api.auth.authLogoutPost().catch(() => null);
    await cookieStore.delete(CURRENT_USER_ID_COOKIE).catch(() => null);
    await cookieStore.delete(CURRENT_USER_NAME_COOKIE).catch(() => null);
    await cookieStore.delete(CURRENT_USER_IS_DEBUG_COOKIE).catch(() => null);
}