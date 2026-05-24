import {redirect} from "react-router";
import Auth from "../data/Auth.ts";
import type {MiddlewareArgs, MiddlewareNext} from "../misc";

export async function dashboardMiddleware(
    {}: MiddlewareArgs,
    next: MiddlewareNext
) : Promise<unknown> {
    const user = await Auth.getCurrentUser();

    if (!user) {
        // TODO: implement dashboard when the DB gets implemented
        throw redirect("/login");
    }

    await next();

    return undefined;
}