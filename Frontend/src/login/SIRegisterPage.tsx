import {Form, Link} from "react-router";
import {FORM_EMAIL, FORM_PASSWORD, FORM_USERNAME} from "./forms.ts";
import {Background} from "../components/Background.tsx";

// Icons

const IconUser = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5 shrink-0">
        <circle cx="12" cy="8" r="4" />
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
    </svg>
);

const IconMail = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5 shrink-0">
        <rect x="2" y="4" width="20" height="16" rx="2" />
        <path d="M2 7l10 7 10-7" />
    </svg>
);

const IconLock = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5 shrink-0">
        <rect x="5" y="11" width="14" height="10" rx="2" />
        <path d="M8 11V7a4 4 0 0 1 8 0v4" />
        <circle cx="12" cy="16" r="1.5" fill="currentColor" stroke="none" />
    </svg>
);


export function SIRegisterPage() {
    // TODO: Account creation page functionality, should also probably redirect if logged in?

    return (
    <Background>
            <div className="w-full max-w-md
                bg-[var(--color-si-card-bg)]
                border-5 border-[var(--color-si-card-border)]
                rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">

            <Form className="flex flex-col gap-5">

                {/* Username */}
                <div className="flex flex-col gap-1.5">
                    <label htmlFor={FORM_USERNAME} className="text-sm font-medium text-[var(--color-si-label)]">
                        Podaj swoją nazwę użytkownika:
                    </label>
                    <div className="flex items-center gap-3
                            border border-[var(--color-si-input-border)]
                            rounded-lg px-3 py-2.5
                            bg-[var(--color-si-input-bg)] transition-colors">
                            <span className="text-[var(--color-si-input-icon)]"><IconUser /></span>
                            <input
                                id={FORM_USERNAME}
                                type="text"
                                name={FORM_USERNAME}
                                placeholder="Nazwa użytkownika"
                                className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                            />
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
                            <span className="text-[var(--color-si-input-icon)]"><IconMail /></span>
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
                            <span className="text-[var(--color-si-input-icon)]"><IconLock /></span>
                            <input
                                id={FORM_PASSWORD}
                                type="password"
                                name={FORM_PASSWORD}
                                placeholder="Hasło"
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
                            value="Zarejestruj się"/>
                    </div>
                </div>
            </Form>
        </div>



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