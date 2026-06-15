import {Link} from "react-router";
import {Background} from "../components/Background.tsx";

export function SIForgotPassword() {
    // TODO: Password reset page, should also redirect if already logged in?

    return <Background>
        <div>
        <div>
            <h1>Forgot password</h1>
        </div>
        <div>
            <Link to="/">Wróć na stronę główną</Link>
        </div>
    </div></Background>
}