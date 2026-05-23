import {Form, Link} from "react-router";

export default function SILoginPage() {
    return <div className={`bg-purple-400 text-black`}>
        <Form>
            <h2>Logowanie</h2>
            <div>
                <label htmlFor="login">Login:</label>
                <input type="text" name="login"/>
            </div>
            <div>
                <label htmlFor="password">Hasło:</label>
                <input type="password" name="password"/>
            </div>
            <div>
                <input type="checkbox" name="remember_me"/>
                <label htmlFor="remember_me">Zapamiętaj mnie</label>

                <input className="cursor-pointer" type="submit" value="Zaloguj się"/>
            </div>
        </Form>
        <div>
            <Link to="/register">Zarejestruj się</Link>
        </div>
    </div>
}