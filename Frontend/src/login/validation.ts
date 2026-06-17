export const DISALLOWED_CHARS: RegExp = /[^\p{Ll}\d\- ]| {2,}|-{2,}|^[- ]|[- ]$/iu;

/**
 * Validates whether the given string can be used in a username, first name etc.
 *
 * The naming rules are as follows:
 * - ALLOWS only letters (Unicode "Letter" group), spaces (` `) and hyphens (`-`).
 * - DISALLOWS repeated spaces and hyphens.
 * - DISALLOWS spaces and hyphens at the beginning or end of the string.
 *
 * @param name The string to be tested.
 * @returns `true` if the string can be a valid username.
 */
export function validateName(name: string): boolean {
    return !DISALLOWED_CHARS.test(name);
}