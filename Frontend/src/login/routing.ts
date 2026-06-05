import {redirect} from "react-router";
import type {MiddlewareArgs, MiddlewareNext} from "../misc";
import {FORM_USERNAME, FORM_LOGOUT, FORM_PASSWORD, FORM_REMEMBER_ME} from "./forms.ts";
import {attemptLogin, attemptLogout, getAuthState} from "../data/auth.ts";

export interface LoginActionResult {
    ok: boolean,
    error: "invalid_credentials" | "invalid_data"
}

export async function loginMiddleware(
    {request}: MiddlewareArgs,
    next: MiddlewareNext
) : Promise<unknown> {
    const urlParams = new URL(request.url).searchParams;

    if (urlParams.has(FORM_LOGOUT)) {
        await attemptLogout();
    } else {
        const user = await getAuthState();
        if (user) {
            throw redirect("/dashboard");
        }
    }

    return await next();
}

export async function loginFormAction(
    {request}: MiddlewareArgs
) : Promise<unknown> {
    const formData = await request.formData();

    const login = formData.get(FORM_USERNAME)?.toString();
    const password = formData.get(FORM_PASSWORD)?.toString();
    const remember = Boolean(formData.get(FORM_REMEMBER_ME));

    if (login && password) {
        const loginSuccessful = await attemptLogin(login, password, remember);

        if (loginSuccessful) {
            return redirect("/dashboard");
        } else {
            return { ok: false, error: "invalid_credentials" } satisfies LoginActionResult;
        }
    } else {
        return { ok: false, error: "invalid_data" } satisfies LoginActionResult;
    }
}
