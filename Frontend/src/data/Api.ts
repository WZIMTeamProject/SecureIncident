import {
    AuthApi,
    Configuration,
    IncidentsApi,
    type Middleware,
    OrganizationApi,
    ProfilesApi,
    ProjectsApi,
    type RefreshResponse,
    type ResponseContext,
    RolesApi,
    UsersApi
} from "../api";
import {BEARER_AUTH_COOKIE} from "./cookies.ts";
import {clearClientAuthCookies, setBearerAuthCookie} from "./auth.ts";

/**
 * Shared in-flight refresh promise. Concurrent 401s collapse onto this single
 * `POST /auth/refresh` call (single-flight) so the rotating refresh token is only
 * consumed once per wave of failures. Reset in `finally` so the next wave refreshes.
 */
let refreshInFlight: Promise<RefreshResponse> | null = null;

function refreshSession(): Promise<RefreshResponse> {
    if (refreshInFlight === null) {
        refreshInFlight = Api.auth.authRefreshPost().finally(() => {
            refreshInFlight = null;
        });
    }
    return refreshInFlight;
}

/**
 * On a 401 from any authenticated request, silently rotate the session via the
 * HttpOnly refresh cookie and replay the original request exactly once with a
 * freshly minted access token.
 */
const silentRefreshMiddleware: Middleware = {
    post: async ({url, init, response}: ResponseContext): Promise<Response | void> => {
        if (response.status !== 401) {
            return;
        }

        // Never intercept the endpoints that establish or rotate the session itself:
        // /auth/refresh would recurse, /auth/login must surface its own 401
        // (wrong credentials), and /auth/me is the initial auth probe used by
        // getAuthState() — a 401 there means the user is anonymous, not that the
        // session expired, so the caller handles it rather than triggering a refresh.
        if (url.includes("/auth/refresh") || url.includes("/auth/login") || url.includes("/auth/me")) {
            return;
        }

        try {
            const refreshed = await refreshSession();
            await setBearerAuthCookie(refreshed.accessToken, refreshed.expiresIn);
        } catch {
            // Refresh failed (missing/expired/reused refresh cookie): the session is
            // unrecoverable. Clear client-visible auth state and bounce to login so the
            // route guards re-evaluate. Guarding on the current path avoids a redirect
            // loop while already on /login (e.g. the pre-login auth probe).
            await clearClientAuthCookies();
            if (typeof window !== "undefined" && window.location.pathname !== "/login") {
                window.location.assign("/login");
            }
            return;
        }

        // Rebuild the Authorization header from the freshly stored token. Replaying the
        // captured init verbatim would resend the stale bearer token and 401 again.
        const freshToken = (await cookieStore.get(BEARER_AUTH_COOKIE))?.value ?? "";
        const retryHeaders = new Headers(init.headers);
        retryHeaders.set("Authorization", `Bearer ${freshToken}`);

        // Re-issue exactly once via the raw fetch (bypassing this middleware) so a
        // still-401 response cannot recurse into an infinite refresh/retry loop.
        return await fetch(url, {...init, headers: retryHeaders});
    },
};

/**
 * Shared API client singleton. Attaches the JWT from the bearer cookie to each request.
 */
export default class Api {
    private static configuration: Configuration = new Configuration({
        basePath: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api", // This is important for CI/CD

        // Send cookies (notably the HttpOnly refresh_token cookie scoped to
        // /api/auth/refresh) with cross-origin requests so silent refresh works.
        credentials: "include",

        middleware: [silentRefreshMiddleware],

        // Unfortunately, the backend currently only reads the token from the Authorization header in HTTP requests.
        // This makes it vulnerable to XSS, since I have to make the token readable through JS to be able to
        // manually paste it to each API request.
        accessToken: async (cookieName) => {
            if (!cookieName) { return ""; }
            return (await cookieStore.get(cookieName))?.value ?? "";
        }
    });

    static auth: AuthApi = new AuthApi(Api.configuration);
    static incidents: IncidentsApi = new IncidentsApi(Api.configuration);
    static organization: OrganizationApi = new OrganizationApi(Api.configuration);
    static profiles: ProfilesApi = new ProfilesApi(Api.configuration);
    static projects: ProjectsApi = new ProjectsApi(Api.configuration);
    static roles: RolesApi = new RolesApi(Api.configuration);
    static users: UsersApi = new UsersApi(Api.configuration);

    // add more API's from /api when needed
}
