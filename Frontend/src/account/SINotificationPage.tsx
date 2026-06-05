import {Link, useLoaderData} from "react-router";
import type {AuthState} from "../data/auth.ts";

export function SINotificationPage() {
    const authState = useLoaderData<AuthState>();

    return <div>
        <div>{authState.name}'s Notifications</div>
        <Link to={"/account"}><i>Wróć</i></Link>
    </div>;
}