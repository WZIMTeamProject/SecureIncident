import {Link, useLoaderData} from "react-router";
import type {AuthState} from "../data/auth.ts";

export function SIAccountPage() {
    const authState = useLoaderData<AuthState>();

    return <div>
        <div>{authState.id}</div>
        <div>{authState.name}</div>
        <div>{authState.isDummyUser ? "DEBUG USER" : ""}</div>
        <Link to={`/account/notifications`}><i>Powiadomienia</i></Link>
    </div>
}