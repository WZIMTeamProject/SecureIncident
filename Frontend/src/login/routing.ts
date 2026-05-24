import Auth from "../data/Auth.ts";
import {redirect} from "react-router";
import type {MiddlewareArgs, MiddlewareNext} from "../misc";
import {FORM_USERNAME, FORM_LOGOUT, FORM_PASSWORD, FORM_REMEMBER_ME} from "./forms.ts";

export async function loginMiddleware(
    {request}: MiddlewareArgs,
    next: MiddlewareNext
) : Promise<unknown> {
    const urlParams = new URL(request.url).searchParams;

    if (urlParams.has(FORM_LOGOUT)) {
        await Auth.logout();
    } else {
        // If user is already logged in, redirect to their dashboard
        const user = await Auth.getCurrentUser();

        if (user) {
            throw redirect("/dashboard");
        }
    }

    await next();

    return undefined;
}

export async function loginAction(
    {request}: MiddlewareArgs
) : Promise<unknown> {
    const formData = await request.formData();

    const login = formData.get(FORM_USERNAME)?.toString();
    const password = formData.get(FORM_PASSWORD)?.toString();
    const remember = Boolean(formData.get(FORM_REMEMBER_ME));

    if (login && password) {
        const user = await Auth.login(login, password, remember);

        if (user) {
            return redirect("/dashboard");
        } else {
            // TODO: Notify about failed login attempt
        }
    } else {
        // TODO: Notify about incorrect input data
    }
}
