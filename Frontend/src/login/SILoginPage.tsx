import {Link, useFetcher, useSearchParams} from "react-router";
import {
    FORM_AFTER, FORM_LOGOUT,
    FORM_PASSWORD,
    FORM_REMEMBER_ME,
    FORM_USERNAME,
    FORM_VALUE_AFTER_PASSWORD_RESET,
    FORM_VALUE_AFTER_REGISTER
} from "./forms.ts";
import {Background} from "../components/Background.tsx";

import {IconLock, IconUser} from "../components/icons.tsx";

export function SILoginPage() {
    const fetcher = useFetcher();
    const [searchParams] = useSearchParams();

    const busy = fetcher.state !== "idle";

    const isAfterRegister = searchParams.get(FORM_AFTER) == FORM_VALUE_AFTER_REGISTER;
    const isAfterPasswordReset = searchParams.get(FORM_AFTER) == FORM_VALUE_AFTER_PASSWORD_RESET;
    const isAfterLogout = searchParams.get(FORM_LOGOUT);

    // TODO: Clear credentials on failed login attempts.
    // TODO: Display more helpful errors.

    return (
        <Background>
            {/* Table */}
            <div className="w-full max-w-md
                bg-[var(--color-si-card-bg)]
                border-5 border-[var(--color-si-card-border)]
                rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">

                <fetcher.Form method="POST" className="flex flex-col gap-5">

                    {/* Username */}
                    <div className="flex flex-col gap-1.5">
                        <label htmlFor={FORM_USERNAME} className="text-sm font-medium text-[var(--color-si-label)]">
                            Podaj swoją nazwę użytkownika:
                        </label>
                        <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">

                            <span className="text-[var(--color-si-input-icon)]"><IconUser/></span>
                            <input
                                id={FORM_USERNAME}
                                type="text"
                                name={FORM_USERNAME}
                                placeholder="Nazwa użytkownika"
                                className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                            />
                        </div>
                    </div>

                    {/* Password */}
                    <div className="flex flex-col gap-1.5">
                        <label htmlFor={FORM_PASSWORD} className="text-sm font-medium text-[var(--color-si-label)]">
                            Podaj hasło:
                        </label>
                        <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">

                            <span className="text-[var(--color-si-input-icon)]"><IconLock/></span>
                            <input
                                id={FORM_PASSWORD}
                                type="password"
                                name={FORM_PASSWORD}
                                placeholder="Hasło"
                                className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                            />
                        </div>
                    </div>

                    {/* REMEMBER ME and Submit */}
                    <div className="flex items-center justify-between">
                        <label htmlFor={FORM_REMEMBER_ME}
                               className="flex items-center gap-2 text-sm text-[var(--color-si-label)] cursor-pointer">
                            <input
                                id={FORM_REMEMBER_ME}
                                type="checkbox"
                                name={FORM_REMEMBER_ME}
                                className="w-4 h-4 bg-[var(--color-si-input-bg)] accent-[var(--color-si-btn)] cursor-pointer"
                            />
                            Zapamiętaj mnie
                        </label>

                        <input
                            type="submit"
                            value={busy ? "Logowanie..." : "Zaloguj się"}
                            disabled={busy}
                            className="px-6 py-2
                                    bg-[var(--color-si-btn)] 
                                    hover:bg-[var(--color-si-btn-hover)]
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                        />
                    </div>

                </fetcher.Form>
            </div>


            {/* Errors and Messages */}
            {fetcher.data?.error && (
                <p className="text-red-500 dark:text-red-400 text-sm">{fetcher.data.error}</p>
            )}
            {isAfterRegister && (
                <p className="text-green-500 dark:text-green-400 text-sm">Zarejestrowano poprawnie. Możesz się
                    zalogować.</p>
            )}
            {isAfterPasswordReset && (
                <p className="text-green-500 dark:text-green-400 text-sm">Hasło zmienione poprawnie. Możesz się
                    zalogować.</p>
            )}
            {isAfterLogout && (
                <p className="text-green-500 dark:text-green-400 text-sm">Wylogowano pomyślnie!</p>
            )}

            {/* Links */}
            <div className="flex flex-col items-center gap-2 text-sm">
                <Link to="/login/forgot_password"
                      className="underline text-[var(--color-si-link)] hover:opacity-75 transition-opacity">
                    Nie pamiętasz hasła?
                </Link>
                <Link to="/login/register"
                      className="underline text-[var(--color-si-link)] hover:opacity-75 transition-opacity">
                    Zarejestruj się →
                </Link>
                <Link to="/" className="underline text-[var(--color-si-link)] hover:opacity-75 transition-opacity">
                    Powrót do strony głównej
                </Link>
            </div>
        </Background>

    );
}
