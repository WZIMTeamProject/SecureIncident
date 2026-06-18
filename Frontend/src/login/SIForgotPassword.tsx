import {Link, useFetcher} from "react-router";
import {FORM_USERNAME} from "./forms.ts";
import {Background} from "../components/Background.tsx";
import {IconUser} from "../components/icons.tsx";

export function SIForgotPassword() {
    const fetcher = useFetcher();
    const busy = fetcher.state != "idle";
    const isPostSend = fetcher.data?.ok;

    // TODO: Make it more obvious the page is about resetting the password

    return (
        <div className="min-h-screen flex flex-col bg-(--color-si-page-bg) transition-colors duration-300">
            <Background>
                <div className="w-full max-w-md
                    bg-(--color-si-card-bg)
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">

                    <fetcher.Form method="POST" className="flex flex-col gap-5" hidden={isPostSend}>
                        {/* Username */}
                        <div className="flex flex-col gap-1.5">
                            <label htmlFor={FORM_USERNAME} className="text-sm font-medium text-(--color-si-label)">
                                Podaj swój e-mail lub nazwę użytkownika:
                            </label>
                            <div className="flex items-center gap-3
                                border border-(--color-si-input-border)
                                rounded-lg px-3 py-2.5
                                bg-(--color-si-input-bg) transition-colors">
                                <span className="text-(--color-si-input-icon)"><IconUser/></span>
                                <input
                                    id={FORM_USERNAME}
                                    type="text"
                                    name={FORM_USERNAME}
                                    placeholder="Email lub Nazwa użytkownika"
                                    className="flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)"
                                />
                            </div>
                        </div>

                        {/* Submit */}
                        <div className={`flex items-center justify-between`}>
                            <span/>

                            <input
                                type="submit"
                                value={busy ? "Wysyłanie..." : "Wyślij"}
                                disabled={busy}
                                className="px-6 py-2
                                    bg-(--color-si-btn)
                                    hover:bg-(--color-si-btn-hover)
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                            />
                        </div>
                    </fetcher.Form>
                    <div className="flex flex-col gap-5" hidden={!isPostSend}>
                        <p className="text-lg font-bold text-(--color-si-input-text)">
                            Wysłano zapytanie
                        </p>
                        <span className="text-sm font-medium text-(--color-si-label)">
                            Jeżeli podane konto jest prawidłowe, otrzymasz wiadomość e-mail z linkiem do resetu hasła.
                        </span>
                    </div>
                </div>


                {/* Links */}
                <div className="flex flex-col items-center gap-2 text-sm">
                    <Link to="/login"
                          className="underline text-(--color-si-link) hover:opacity-75 transition-opacity">
                        Powrót do logowania
                    </Link>
                    <Link to="/" className="underline text-(--color-si-link) hover:opacity-75 transition-opacity">
                        Powrót do strony głównej
                    </Link>
                </div>
            </Background>
        </div>
    )
}