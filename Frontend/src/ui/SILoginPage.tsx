import {Form, Link} from "react-router";

export default function SILoginPage() {
    return <div>
        <div className={`w-lg p-2 bg-purple-400 text-black`}>
            <Form method="post" navigate={false}>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor="login">Podaj swoją nazwę użytkownika:</label>
                    <input type="text" name="login" className={`bg-white`}/>
                </div>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor="password">Podaj hasło:</label>
                    <input type="password" name="password" className={`bg-white`}/>
                </div>
                <div className={`m-2 flex`}>
                    <div className={`grow`}>
                        <input type="checkbox" name="remember_me"/>
                        <label htmlFor="remember_me"> Zapamiętaj mnie</label>
                    </div>

                    <div>
                        <input className={`p-2 cursor-pointer bg-purple-500 text-white underline`} type="submit" value="Zaloguj się"/>
                    </div>
                </div>
            </Form>
        </div>
        <div>
            <Link to="/register">Zarejestruj się</Link>
        </div>
        <div>
            <Link to="/forgot_password">Nie pamiętasz hasła?</Link>
        </div>
        <div>
            <Link to="/">Powrót do strony głównej</Link>
        </div>
    </div>
}