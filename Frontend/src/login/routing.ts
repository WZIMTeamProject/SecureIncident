import {type ActionFunction, type MiddlewareFunction, redirect} from "react-router";
import {
    FORM_EMAIL, FORM_FIRST_NAME, FORM_JUST_REGISTERED, FORM_LAST_NAME,
    FORM_LOGOUT,
    FORM_PASSWORD,
    FORM_PASSWORD_REPEAT,
    FORM_REMEMBER_ME,
    FORM_USERNAME
} from "./forms.ts";
import {attemptLogin, attemptLogout, attemptRegistration, AuthRouterContext} from "../data/auth.ts";
import {validateName} from "./validation.ts";

export interface RegisterActionResult {
    error: "invalid_data" | "repeat_password_mismatch" | "username_taken" | "username_too_short" | "unknown",
}

export interface LoginActionResult {
    error: "invalid_credentials" | "invalid_data",
}

/**
 * When used as routing middleware, redirects the user to their dashboard if they try accessing this page.
 */
export const redirectToDashboardMiddleware: MiddlewareFunction = async ({context}, next) => {
    if (context.get(AuthRouterContext)) {
        throw redirect("/dashboard");
    }

    return await next();
};

export const logoutMiddleware: MiddlewareFunction = async ({request, context}, next) => {
    const urlParams = new URL(request.url).searchParams;

    if (urlParams.has(FORM_LOGOUT)) {
        await attemptLogout();
        context.set(AuthRouterContext, null);
    }

    return await next();
}

export const loginFormAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    const login = formData.get(FORM_USERNAME)?.toString();
    const password = formData.get(FORM_PASSWORD)?.toString();
    const remember = Boolean(formData.get(FORM_REMEMBER_ME));

    if (login && password) {
        const loginSuccessful = await attemptLogin(login, password, remember);

        if (loginSuccessful) {
            return redirect("/dashboard");
        } else {
            return {error: "invalid_credentials"} satisfies LoginActionResult;
        }
    } else {
        return {error: "invalid_data"} satisfies LoginActionResult;
    }
};

export const registerFormAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    // I feel like these should be tested if they contain weird Unicode characters
    const firstName = formData.get(FORM_FIRST_NAME)?.toString()?.trim();
    const lastName = formData.get(FORM_LAST_NAME)?.toString()?.trim();
    const username = formData.get(FORM_USERNAME)?.toString()?.trim();
    const password = formData.get(FORM_PASSWORD)?.toString()?.trim();
    const password_repeat = formData.get(FORM_PASSWORD_REPEAT)?.toString()?.trim();
    const email = formData.get(FORM_EMAIL)?.toString()?.trim();

    if (username && password && email && firstName && lastName) {
        if (password !== password_repeat) {
            return {error: "repeat_password_mismatch"} satisfies RegisterActionResult;
        }

        const namesAreValid = validateName(username) && validateName(lastName) && validateName(firstName);
        if (!namesAreValid) {
            return {error: "invalid_data"} satisfies RegisterActionResult;
        }

        const registrationResult = await attemptRegistration(firstName, lastName, username, email, password);
        if (registrationResult.success) {
            return redirect(`/login?${FORM_JUST_REGISTERED}`);
        } else {
            switch (registrationResult.errorCause) {
                case "username_or_email_taken":
                    return {error: "username_taken"} satisfies RegisterActionResult;
                case "username_too_short":
                    return {error: "username_too_short"} satisfies RegisterActionResult;
                default:
                    return {error: "unknown"} satisfies RegisterActionResult;
            }
        }
    } else {
        return {error: "invalid_data"} satisfies RegisterActionResult;
    }
};