import {Link} from "react-router";
import {FORM_LOGOUT} from "../login/forms.ts";

export function SIDashboard() {
    return <div>
        <div>
            <h1>Dashboard</h1>
        </div>
        <div>
            <Link to={{
                pathname: "/login",
                search: `?${FORM_LOGOUT}=true`
            }}>
                Wyloguj
            </Link>
        </div>
    </div>
}