import {Form, Link} from "react-router";
import {FORM_EMAIL, FORM_PASSWORD, FORM_USERNAME} from "./forms.ts";

export function SIRegisterPage() {
    // TODO: Account creation page functionality, should also probably redirect if logged in?

    return <div>
        <div className={`w-lg p-2 bg-purple-400 text-black`}>
            <Form>
                <div className={`m-2 flex flex-col`}>
                    <label htmlFor={FORM_USERNAME}>Podaj swoją nazwę użytkownika:</label>
                    <input type="text" name={FORM_USERNAME} className={`bg-white`}/>
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
                            value="Zarejestruj się"/>
                    </div>
                </div>
            </Form>
        </div>
        <div>
            <Link to="/login">Mam już konto</Link>
        </div>
        <div>
            <Link to="/">Powrót do strony głównej</Link>
        </div>
    </div>
}