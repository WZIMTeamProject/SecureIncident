/**
 * Cookie names used for auth, theme, and session state.
 * Uses the Cookie Store API (`cookieStore`); legacy browsers are not supported.
 */
// This file names of cookies stored throughout the application.
// We also use the `cookieStore` for cookie management, so we officially don't support browsers from before 2025 ;)

export const CURRENT_USER_NAME_COOKIE = "currentUser";
export const CURRENT_USER_ORGANIZATION_COOKIE = "currentUserOrganization";
export const CURRENT_USER_ID_COOKIE = "currentUserId";
export const CURRENT_USER_IS_DEBUG_COOKIE = "currentUserIsDebug";

export const THEME_PREFERENCE = "theme";
export const THEME_PREFERENCE_DARK = "dark";
export const THEME_PREFERENCE_LIGHT = "light";

/**
 * Default name for the authentication cookie taken from the auto-generated API bindings.
 * Don't change this string unless the cookie used by the bindings also changes.
 */
export const BEARER_AUTH_COOKIE = "bearerAuth";
