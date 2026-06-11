import {type ActionFunction, type MiddlewareFunction, redirect} from "react-router";
import {FORM_USERNAME, FORM_LOGOUT, FORM_PASSWORD, FORM_REMEMBER_ME} from "./forms.ts";
import {attemptLogin, attemptLogout, AuthRouterContext} from "../data/auth.ts";

export interface LoginActionResult {
    ok: boolean,
    error: "invalid_credentials" | "invalid_data"
}

export const loginMiddleware: MiddlewareFunction = async ({request, context}, next) => {
    const urlParams = new URL(request.url).searchParams;
    const user = context.get(AuthRouterContext);

    if (urlParams.has(FORM_LOGOUT)) {
        await attemptLogout();
        context.set(AuthRouterContext, null);
    } else if (user) {
        throw redirect("/dashboard");
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
            return { ok: false, error: "invalid_credentials" } satisfies LoginActionResult;
        }
    } else {
        return { ok: false, error: "invalid_data" } satisfies LoginActionResult;
    }
}
