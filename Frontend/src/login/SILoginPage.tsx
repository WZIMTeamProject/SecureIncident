import {Link, useFetcher} from "react-router";
import {FORM_PASSWORD, FORM_REMEMBER_ME, FORM_USERNAME} from "./forms.ts";

export function SILoginPage() {
    const fetcher = useFetcher();

    return <div>
        <div className={`w-lg p-2 bg-purple-400 text-black`}>
            <fetcher.Form method="POST">
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_USERNAME}>Podaj swoją nazwę użytkownika:</label>
                    <input type="text" name={FORM_USERNAME} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_PASSWORD}>Podaj hasło:</label>
                    <input type="password" name={FORM_PASSWORD} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex`}>
                    <div className={`grow`}>
                        <input type="checkbox" name={FORM_REMEMBER_ME}/>
                        <label htmlFor={FORM_REMEMBER_ME}> Zapamiętaj mnie</label>
                    </div>

                    <div>
                        <input
                            className={`p-2 cursor-pointer bg-purple-500 text-white underline`}
                            type="submit"
                            value={fetcher.state != "idle" ? "Logowanie..." : "Zaloguj się"}/>
                    </div>
                </div>
            </fetcher.Form>
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

        <div>
            {fetcher.data ? fetcher.data.error : undefined}
        </div>
    </div>
}