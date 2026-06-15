import {Link, useFetcher} from "react-router";
import {FORM_EMAIL, FORM_FIRST_NAME, FORM_LAST_NAME, FORM_PASSWORD, FORM_USERNAME} from "./forms.ts";
import {Background} from "../components/Background.tsx";

export function SIRegisterPage() {
    const fetcher = useFetcher();
    const busy = fetcher.state !== "idle";

    return <Background>
        <div className={`w-lg p-2 bg-purple-400 text-black`}>
            <fetcher.Form method="POST">
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_USERNAME}>Podaj swoją nazwę użytkownika:</label>
                    <input type="text" name={FORM_USERNAME} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_FIRST_NAME}>Podaj swoje imię:</label>
                    <input type="text" name={FORM_FIRST_NAME} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_LAST_NAME}>Podaj swoje nazwisko:</label>
                    <input type="text" name={FORM_LAST_NAME} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_EMAIL}>Podaj adres e-mail:</label>
                    <input type="email" name={FORM_EMAIL} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_PASSWORD}>Podaj hasło:</label>
                    <input type="password" name={FORM_PASSWORD} className={`bg-white`}/>
                </div>
                <div className={`m-2 flex`}>
                    <div>
                        <input
                            className={`p-2 cursor-pointer bg-purple-500 text-white underline`}
                            type="submit"
                            value={busy ? "Rejestrowanie..." : "Zarejestruj się"}
                            disabled={busy}
                            />
                    </div>
                </div>
            </fetcher.Form>
        </div>
        <div>
            <Link to="/login">Mam już konto</Link>
        </div>
        <div>
            <Link to="/">Powrót do strony głównej</Link>
        </div>
    </Background>
}