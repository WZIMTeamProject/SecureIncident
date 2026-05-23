import {Link} from "react-router";

export default function SIPageNotFound() {
    return <div>
        <div>
            <h1 className={`text-4xl`}>404 not found</h1>
        </div>
        <div>
            <Link to="/">Wróć na stronę główną</Link>
        </div>
    </div>
}