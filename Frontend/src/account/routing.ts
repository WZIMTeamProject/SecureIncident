import {type ActionFunction} from "react-router";
import {
    FORM_ACTION,
    FORM_ACTION_CHANGE_PASSWORD,
    FORM_ACTION_UPDATE_PROFILE,
    FORM_BIO,
    FORM_CURRENT_PW,
    FORM_NEW_PW,
    FORM_PICTURE_URL,
} from "./forms.ts";
import Api from "../data/Api.ts";
import {ResponseError} from "../api";

export interface AccountActionResult {
    ok: boolean;
    error?: string;
    field?: "current_password" | "new_password";
}

/**
 * Reads the FastAPI `detail` string from an error response without throwing.
 * Used to distinguish the two different 400 causes on change-password
 * (wrong current password vs. new password equal to the current one), which
 * the backend reports with the same status code.
 */
async function readErrorDetail(error: unknown): Promise<string | null> {
    if (!(error instanceof ResponseError)) {
        return null;
    }

    try {
        const body = await error.response.json();
        const detail = body?.detail;
        return typeof detail === "string" ? detail : null;
    } catch {
        return null;
    }
}

export const accountAction: ActionFunction = async ({request}): Promise<AccountActionResult> => {
    const formData = await request.formData();

    const accountAction = formData.get(FORM_ACTION)?.toString();
    if (!accountAction || request.method !== "POST") {
        return {ok: false, error: "Nieprawidłowe żądanie."};
    }

    if (accountAction === FORM_ACTION_UPDATE_PROFILE) {
        const bio = formData.get(FORM_BIO)?.toString()?.trim() ?? "";
        const pictureUrl = formData.get(FORM_PICTURE_URL)?.toString()?.trim() ?? "";

        try {
            await Api.profiles.profilesMePatch({
                updateProfileRequest: {
                    bio: bio,
                    profilePictureUrl: pictureUrl || null,
                },
            });

            return {ok: true};
        } catch {
            return {ok: false, error: "Nie udało się zapisać profilu."};
        }
    }

    if (accountAction === FORM_ACTION_CHANGE_PASSWORD) {
        const currentPassword = formData.get(FORM_CURRENT_PW)?.toString() ?? "";
        const newPassword = formData.get(FORM_NEW_PW)?.toString() ?? "";

        if (!currentPassword || !newPassword) {
            return {ok: false, error: "Wszystkie pola są wymagane."};
        }

        try {
            await Api.auth.authChangePasswordPost({
                changePasswordRequest: {
                    currentPassword: currentPassword,
                    newPassword: newPassword,
                },
            });

            return {ok: true};
        } catch (ex) {
            let status = 0;
            if (ex instanceof ResponseError) {
                status = ex.response.status;
            }

            switch (status) {
                case 400: {
                    // The backend returns 400 both for an incorrect current password
                    // ("Current password is incorrect") and when the new password equals
                    // the current one ("New password must be different from the current
                    // password"). Both strings contain "current", so we discriminate on the
                    // distinguishing token: "different" (new==current) vs "incorrect" (wrong
                    // current password). When the detail is unavailable, surface a neutral
                    // message that does not mis-blame the current-password field.
                    const detail = (await readErrorDetail(ex))?.toLowerCase() ?? "";

                    const newEqualsCurrent =
                        detail.includes("different") ||
                        detail.includes("różni") ||
                        detail.includes("rozni") ||
                        detail.includes("identyczne");

                    if (newEqualsCurrent) {
                        return {
                            ok: false,
                            field: "new_password",
                            error: "Nowe hasło musi różnić się od obecnego.",
                        };
                    }

                    const currentIncorrect =
                        detail.includes("incorrect") ||
                        detail.includes("nieprawid") ||
                        detail.includes("aktualne");

                    if (currentIncorrect) {
                        return {
                            ok: false,
                            field: "current_password",
                            error: "Nieprawidłowe aktualne hasło.",
                        };
                    }

                    return {ok: false, error: "Nie udało się zmienić hasła. Sprawdź wprowadzone dane."};
                }
                case 422:
                    return {
                        ok: false,
                        field: "new_password",
                        error: "Nowe hasło jest zbyt słabe lub za krótkie.",
                    };
                case 401:
                    return {ok: false, error: "Sesja wygasła. Zaloguj się ponownie."};
                default:
                    return {ok: false, error: "Nie udało się zmienić hasła."};
            }
        }
    }

    return {ok: false, error: "Nieznana operacja."};
};
