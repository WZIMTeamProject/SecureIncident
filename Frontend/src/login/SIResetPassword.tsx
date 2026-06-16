import {Background} from "../components/Background.tsx";
import {useFetcher, useSearchParams} from "react-router";
import {FORM_PASSWORD, FORM_PASSWORD_REPEAT, FORM_RESET_TOKEN} from "./forms.ts";
import {IconLock} from "../components/icons.tsx";

export function SIResetPassword() {
    const fetcher = useFetcher();
    const [searchParams] = useSearchParams();

    const busy = fetcher.state != "idle";
    const resetToken = searchParams.get("token");

    // TODO: Make it more obvious the page is about resetting the password

    return (
        <div className="min-h-screen flex flex-col bg-[var(--color-si-page-bg)] transition-colors duration-300">
            <Background>
                <div className="w-full max-w-md
                    bg-[var(--color-si-card-bg)]
                    border-5 border-[var(--color-si-card-border)]
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">

                    <fetcher.Form method="POST" className="flex flex-col gap-5">
                        {/* Password */}
                        <div className="flex flex-col gap-1.5">
                            <label htmlFor={FORM_PASSWORD} className="text-sm font-medium text-[var(--color-si-label)]">
                                Podaj nowe hasło:
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

                        {/* Repeat Password */}
                        <div className="flex flex-col gap-1.5">
                            <label
                                htmlFor={FORM_PASSWORD_REPEAT}
                                className="text-sm font-medium text-[var(--color-si-label)]">
                                Powtórz nowe hasło:
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
                                    placeholder="Powtórz Hasło"
                                    className="flex-1 bg-transparent outline-none text-sm text-[var(--color-si-input-text)]"
                                />
                            </div>
                        </div>

                        {/* Reset token passed to the query */}
                        <input
                            id={FORM_RESET_TOKEN}
                            type="hidden"
                            name={FORM_RESET_TOKEN}
                            value={resetToken ?? undefined}
                        />

                        {/* Submit */}
                        <div className={`flex items-center justify-between`}>
                            <span/>

                            <input
                                type="submit"
                                value={busy ? "Wysyłanie..." : "Wyślij"}
                                disabled={busy}
                                className="px-6 py-2
                                    bg-[var(--color-si-btn)]
                                    hover:bg-[var(--color-si-btn-hover)]
                                    disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200"
                            />
                        </div>
                    </fetcher.Form>
                </div>

                {fetcher.data?.error && (
                    <p className="text-red-500 dark:text-red-400 text-sm">{fetcher.data.error}</p>
                )}
            </Background>
        </div>
    );
}