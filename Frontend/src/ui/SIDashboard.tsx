import {Link} from "react-router";

export default function SIDashboard() {
    return <div>
        <div>
            <h1>Dashboard</h1>
        </div>
        <div>
            <Link to={{
                pathname: "/login",
                search: "?logout=true"
            }}>Wyloguj</Link>
        </div>
    </div>
}