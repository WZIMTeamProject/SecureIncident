import {Link} from "react-router";

export function SIToolbar() {
    return <div className={`bg-purple-600 p-2 flex gap-2`}>
        <div><Link to={`/`}>Strona Główna</Link></div>
        <div><Link to={`/login`}>Logowanie</Link></div>
    </div>
}