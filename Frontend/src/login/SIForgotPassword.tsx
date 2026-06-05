import {Link} from "react-router";

export function SIForgotPassword() {
    // TODO: Password reset page, should also redirect if already logged in?

    return <div>
        <div>
            <h1>Forgot password</h1>
        </div>
        <div>
            <Link to="/">Wróć na stronę główną</Link>
        </div>
    </div>
}