import {Link} from "react-router";

export default function SIToolbar() {
    return <div className={`flex gap-2 p-2 bg-purple-600`}>
        <div><Link to={`/`}>Strona Główna</Link></div>
        <div><Link to={`/login`}>Logowanie</Link></div>
    </div>
}