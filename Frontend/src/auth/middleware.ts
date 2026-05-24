import {redirect} from "react-router";
import Auth from "./Auth.ts";

export async function dashboardMiddleware({}, next: () => Promise<unknown>) {
    const user = await Auth.getCurrentUser()

    if (!user) {
        // TODO: implement dashboard when the DB gets implemented
        throw redirect("/login")
    }

    await next()
}

export async function loginMiddleware({ request } : { request: Request }, next: () => Promise<unknown>) {
    const urlParams = new URL(request.url).searchParams

    if (urlParams.has("logout")) {
        await Auth.logout()
    } else {
        // If user is already logged in, redirect to their dashboard
        const user = await Auth.getCurrentUser()

        if (user) {
            throw redirect("/dashboard")
        }
    }

    await next()
}

export async function loginAction({ request } : { request: Request }) {
    const formData = await request.formData()

    const login = formData.get("login")?.toString()
    const password = formData.get("password")?.toString()
    const remember = Boolean(formData.get("remember_me"))

    if (login && password) {
        const user = await Auth.login(login, password, remember)

        if (user) {
            return redirect("/dashboard")
        } else {
            // TODO: Notify about failed login attempt
        }
    } else {
        // TODO: Notify about incorrect input data
    }
}