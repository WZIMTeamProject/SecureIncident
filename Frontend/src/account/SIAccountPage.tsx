import {Link, useFetcher, useLoaderData} from "react-router";
import {type FormEvent, useEffect, useRef, useState} from "react";
import type {AuthState} from "../data/auth.ts";
import type {UserProfile} from "../data/profile.ts";
import {IconImage, IconLock, IconLockCheck, IconUser} from "../components/icons.tsx";
import {
    FORM_ACTION,
    FORM_ACTION_CHANGE_PASSWORD,
    FORM_ACTION_UPDATE_PROFILE,
    FORM_BIO,
    FORM_CONFIRM_PW,
    FORM_CURRENT_PW,
    FORM_NEW_PW,
    FORM_PICTURE_URL,
} from "./forms.ts";
import type {AccountActionResult} from "./routing.ts";
import {Background} from "../components/Background.tsx";

const CARD_CLASS = "border-5 border-(--color-si-card-border) rounded-2xl shadow-lg px-5 sm:px-8 py-8 transition-colors duration-300";
const LABEL_CLASS = "text-sm font-medium text-(--color-si-label)";
const INPUT_SHELL_CLASS = "flex items-center gap-3 border border-(--color-si-input-border) rounded-lg px-3 py-2.5 bg-(--color-si-input-bg) transition-colors";
const FIELD_CLASS = "flex-1 bg-transparent outline-none text-sm text-(--color-si-input-text)";
const BUTTON_CLASS = "px-6 py-2 min-h-11 bg-(--color-si-btn) hover:bg-(--color-si-btn-hover) shadow-lg disabled:opacity-60 text-white text-sm font-semibold rounded-lg cursor-pointer transition-colors duration-200";
const LINK_CLASS = "inline-flex items-center min-h-11 underline text-(--color-si-link) hover:opacity-75 transition-opacity";

export function SIAccountPage() {
    const authState = useLoaderData<AuthState>();
    const [profile, setProfile] = useState<UserProfile | null | undefined>(undefined);

    useEffect(() => {
        let ignore = false;

        authState.getProfile().then((loadedProfile) => {
            if (!ignore) {
                setProfile(loadedProfile);
            }
        });

        return () => {
            ignore = true;
        };
    }, [authState]);

    return (
        <Background>
            <div className="w-full max-w-2xl flex flex-col gap-6">
                <h1 className="text-3xl font-bold text-(--color-si-label)">Ustawienia konta</h1>

                <ProfileSummary profile={profile}/>
                <EditProfileForm profile={profile}/>
                <ChangePasswordForm/>

                <div className="flex flex-wrap gap-4 text-sm">
                    <Link to="/account/notifications" className={LINK_CLASS}>Powiadomienia</Link>
                    <Link to="/dashboard" className={LINK_CLASS}>Wróć do panelu</Link>
                </div>
            </div>
        </Background>
    );
}

interface ProfileSummaryProps {
    profile: UserProfile | null | undefined;
}

function ProfileSummary({profile}: ProfileSummaryProps) {
    if (profile === undefined) {
        return <div className={CARD_CLASS}><h2 className="text-xl font-semibold text-(--color-si-label)">Wczytywanie...</h2></div>;
    }

    if (profile === null) {
        return (
            <div className={CARD_CLASS}>
                <p className="text-red-500 dark:text-red-400 text-sm">Nie udało się wczytać profilu.</p>
            </div>
        );
    }

    return (
        <div className={CARD_CLASS}>
            <div className="flex items-start gap-4">
                {profile.profilePictureURL ? (
                    <img
                        src={profile.profilePictureURL}
                        alt={`Zdjęcie profilowe ${profile.username}`}
                        className="w-16 h-16 rounded-full object-cover shrink-0"
                    />
                ) : (
                    <span
                        aria-hidden="true"
                        className="flex w-16 h-16 items-center justify-center rounded-full shrink-0 bg-(--color-si-input-bg) text-(--color-si-input-icon)"
                    >
                        <IconUser/>
                    </span>
                )}
                <div className="flex flex-col gap-1">
                    <span className="text-xl font-semibold text-(--color-si-label)">{profile.username}</span>
                    <span className="text-sm italic text-(--color-si-input-text)">
                        {profile.bio || "Brak opisu"}
                    </span>
                </div>
            </div>
        </div>
    );
}

interface EditProfileFormProps {
    profile: UserProfile | null | undefined;
}

function EditProfileForm({profile}: EditProfileFormProps) {
    const fetcher = useFetcher<AccountActionResult>();
    const busy = fetcher.state !== "idle";
    const result = fetcher.data;
    const success = result?.ok === true;

    // Re-key the uncontrolled form once the profile loads so the defaultValue
    // prefill takes effect (the form first renders before the async load).
    const formKey = profile ? `loaded-${profile.id}` : "loading";

    return (
        <fetcher.Form key={formKey} method="POST" className={`${CARD_CLASS} flex flex-col gap-4`}>
            <h2 className="text-2xl font-bold text-(--color-si-label)">Edytuj profil</h2>

            <div className="flex flex-col gap-1.5">
                <label htmlFor={FORM_BIO} className={LABEL_CLASS}>Bio:</label>
                <div className={INPUT_SHELL_CLASS}>
                    <textarea
                        id={FORM_BIO}
                        name={FORM_BIO}
                        rows={3}
                        defaultValue={profile?.bio ?? ""}
                        placeholder="Napisz coś o sobie"
                        className={`${FIELD_CLASS} resize-y`}
                    />
                </div>
            </div>

            <div className="flex flex-col gap-1.5">
                <label htmlFor={FORM_PICTURE_URL} className={LABEL_CLASS}>Adres URL zdjęcia profilowego:</label>
                <div className={INPUT_SHELL_CLASS}>
                    <span className="text-(--color-si-input-icon)" aria-hidden="true"><IconImage/></span>
                    <input
                        id={FORM_PICTURE_URL}
                        name={FORM_PICTURE_URL}
                        type="url"
                        defaultValue={profile?.profilePictureURL ?? ""}
                        placeholder="https://..."
                        className={FIELD_CLASS}
                    />
                </div>
            </div>

            <div role="alert" aria-live="polite" className="min-h-5">
                {result && !result.ok && result.error && (
                    <p className="text-red-500 dark:text-red-400 text-sm">{result.error}</p>
                )}
                {success && <p className="text-green-500 dark:text-green-400 text-sm">Zapisano</p>}
            </div>

            <div className="flex justify-end">
                <input type="hidden" name={FORM_ACTION} value={FORM_ACTION_UPDATE_PROFILE}/>
                <input
                    type="submit"
                    value={busy ? "Zapisywanie..." : "Zapisz zmiany"}
                    disabled={busy}
                    className={BUTTON_CLASS}
                />
            </div>
        </fetcher.Form>
    );
}

function ChangePasswordForm() {
    const fetcher = useFetcher<AccountActionResult>();
    const busy = fetcher.state !== "idle";
    const result = fetcher.data;
    const success = result?.ok === true;

    const [clientError, setClientError] = useState<string | null>(null);

    const currentRef = useRef<HTMLInputElement>(null);
    const newRef = useRef<HTMLInputElement>(null);
    const confirmRef = useRef<HTMLInputElement>(null);

    // Clear the password fields once a submission settles (success or error) so
    // they are never left sitting in the DOM. Mirrors the SILoginPage behaviour.
    useEffect(() => {
        if (fetcher.state === "idle" && fetcher.data) {
            if (currentRef.current) currentRef.current.value = "";
            if (newRef.current) newRef.current.value = "";
            if (confirmRef.current) confirmRef.current.value = "";
            currentRef.current?.focus();
        }
    }, [fetcher.state, fetcher.data]);

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        // Client-side confirm-match is UX-only; the backend remains the boundary.
        if (newRef.current?.value !== confirmRef.current?.value) {
            event.preventDefault();
            setClientError("Hasła nie są zgodne");
            return;
        }
        setClientError(null);
    };

    const currentError = result && !result.ok && result.field === "current_password" ? result.error : null;
    const newError = result && !result.ok && result.field === "new_password" ? result.error : null;
    const generalError = result && !result.ok && !result.field ? result.error : null;

    return (
        <fetcher.Form method="POST" onSubmit={onSubmit} className={`${CARD_CLASS} flex flex-col gap-4`}>
            <h2 className="text-2xl font-bold text-(--color-si-label)">Zmień hasło</h2>

            <div className="flex flex-col gap-1.5">
                <label htmlFor={FORM_CURRENT_PW} className={LABEL_CLASS}>Aktualne hasło:</label>
                <div className={INPUT_SHELL_CLASS}>
                    <span className="text-(--color-si-input-icon)" aria-hidden="true"><IconLock/></span>
                    <input
                        ref={currentRef}
                        id={FORM_CURRENT_PW}
                        name={FORM_CURRENT_PW}
                        placeholder="Aktualne hasło"
                        type="password"
                        required={true}
                        className={FIELD_CLASS}
                    />
                </div>
                {currentError && <p className="text-red-500 dark:text-red-400 text-sm">{currentError}</p>}
            </div>

            <div className="flex flex-col gap-1.5">
                <label htmlFor={FORM_NEW_PW} className={LABEL_CLASS}>Nowe hasło:</label>
                <div className={INPUT_SHELL_CLASS}>
                    <span className="text-(--color-si-input-icon)" aria-hidden="true"><IconLock/></span>
                    <input
                        ref={newRef}
                        id={FORM_NEW_PW}
                        name={FORM_NEW_PW}
                        placeholder="Nowe hasło"
                        type="password"
                        required={true}
                        minLength={8}
                        className={FIELD_CLASS}
                    />
                </div>
                {newError && <p className="text-red-500 dark:text-red-400 text-sm">{newError}</p>}
            </div>

            <div className="flex flex-col gap-1.5">
                <label htmlFor={FORM_CONFIRM_PW} className={LABEL_CLASS}>Potwierdź nowe hasło:</label>
                <div className={INPUT_SHELL_CLASS}>
                    <span className="text-(--color-si-input-icon)" aria-hidden="true"><IconLockCheck/></span>
                    <input
                        ref={confirmRef}
                        id={FORM_CONFIRM_PW}
                        name={FORM_CONFIRM_PW}
                        placeholder="Powtórz nowe hasło"
                        type="password"
                        required={true}
                        className={FIELD_CLASS}
                    />
                </div>
            </div>

            <div role="alert" aria-live="polite" className="min-h-5">
                {clientError && <p className="text-red-500 dark:text-red-400 text-sm">{clientError}</p>}
                {generalError && <p className="text-red-500 dark:text-red-400 text-sm">{generalError}</p>}
                {success && <p className="text-green-500 dark:text-green-400 text-sm">Hasło zostało zmienione</p>}
            </div>

            <div className="flex justify-end">
                <input type="hidden" name={FORM_ACTION} value={FORM_ACTION_CHANGE_PASSWORD}/>
                <input
                    type="submit"
                    value={busy ? "Zmienianie..." : "Zmień hasło"}
                    disabled={busy}
                    className={BUTTON_CLASS}
                />
            </div>
        </fetcher.Form>
    );
}
