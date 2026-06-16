import {Link, useFetcher} from "react-router";
import {
    FORM_EMAIL,
    FORM_FIRST_NAME,
    FORM_LAST_NAME,
    FORM_PASSWORD,
    FORM_PASSWORD_REPEAT,
    FORM_USERNAME
} from "./forms.ts";
import {Background} from "../components/Background.tsx";
import {IconLock, IconMail, IconUser} from "../components/icons.tsx";


export function SIRegisterPage() {
    const fetcher = useFetcher();
    const busy = fetcher.state !== "idle";

    // TODO: Clear credentials on failed login attempts.
    // TODO: Add different icons for fields

    return (
        <Background>
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

                    {/* First Name */}
                    <div className={`flex flex-col gap-1.5`}>
                        <label htmlFor={FORM_FIRST_NAME}
                               className="text-sm font-medium text-[var(--color-si-label)]">
                            Podaj swoje imię:
                        </label>
                        <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">

                            <span className="text-[var(--color-si-input-icon)]"><IconUser/></span>
                            <input
                                id={FORM_FIRST_NAME}
                                type="text"
                                name={FORM_FIRST_NAME}
                                placeholder="Imię"
                                className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"/>
                        </div>
                    </div>

                    {/* Last Name */}
                    <div className={`flex flex-col gap-1.5`}>
                        <label htmlFor={FORM_LAST_NAME}
                               className="text-sm font-medium text-[var(--color-si-label)]">
                            Podaj swoje nazwisko:
                        </label>
                        <div className="flex items-center gap-3
                                border border-[var(--color-si-input-border)]
                                rounded-lg px-3 py-2.5
                                bg-[var(--color-si-input-bg)] transition-colors">

                            <span className="text-[var(--color-si-input-icon)]"><IconUser/></span>
                            <input
                                id={FORM_LAST_NAME}
                                type="text"
                                name={FORM_LAST_NAME}
                                placeholder="Nazwisko"
                                className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"/>
                        </div>
                    </div>

                    {/* E-mail */}
                    <div className="flex flex-col gap-1.5">
                        <label htmlFor={FORM_EMAIL} className="text-sm font-medium text-[var(--color-si-label)]">
                            Podaj adres e-mail:
                        </label>
                        <div className="flex items-center gap-3
                            border border-[var(--color-si-input-border)]
                            rounded-lg px-3 py-2.5
                            bg-[var(--color-si-input-bg)] transition-colors">
                            <span className="text-[var(--color-si-input-icon)]"><IconMail/></span>
                            <input
                                id={FORM_EMAIL}
                                type="email"
                                name={FORM_EMAIL}
                                placeholder="Adres e-mail"
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

                    {/* Password Repeat */}
                    <div className="flex flex-col gap-1.5">
                        <label htmlFor={FORM_PASSWORD_REPEAT} className="text-sm font-medium text-[var(--color-si-label)]">
                            Powtórz hasło:
                        </label>
                        <div className="flex items-center gap-3
                            border border-[var(--color-si-input-border)]
                            rounded-lg px-3 py-2.5
                            bg-[var(--color-si-input-bg)] transition-colors">
                            <span className="text-[var(--color-si-input-icon)]"><IconLock/></span>
                            <input
                                id={FORM_PASSWORD_REPEAT}
                                type="password"
                                name={FORM_PASSWORD_REPEAT}
                                placeholder="Powtórz hasło"
                                className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                            />
                        </div>
                    </div>

                    {/* Submit */}
                    <div className={`flex justify-end`}>
                        <div>
                            <input
                                className="px-6 py-2
                                bg-[var(--color-si-btn)]
                                hover:bg-[var(--color-si-btn-hover)]
                                text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                                type="submit"
                                disabled={busy}
                                value={busy ? "Rejestrowanie..." : "Zarejestruj się"}/>
                        </div>
                    </div>
                </fetcher.Form>
            </div>

            {/* Error */}
            {fetcher.data?.error && (
                <p className="text-red-500 dark:text-red-400 text-sm">{fetcher.data.error}</p>
            )}

            {/* Links */}
            <div className="flex flex-col items-center gap-2 text-sm">
                <Link to="/login" className="underline text-[var(--color-si-link)] hover:opacity-75 transition-opacity">
                    Mam już konto</Link>
                <Link to="/" className="underline text-[var(--color-si-link)] hover:opacity-75 transition-opacity">
                    Powrót do strony głównej
                </Link>
            </div>
        </Background>
    );
}