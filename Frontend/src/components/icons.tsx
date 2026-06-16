/**
 * User icon (for the `username` field).
 */
export function IconUser() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5 shrink-0">
        <circle cx="12" cy="8" r="4"/>
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
    </svg>;
}

/**
 * Lock icon (for the `password` field).
 */
export function IconLock() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5 shrink-0">
        <rect x="5" y="11" width="14" height="10" rx="2"/>
        <path d="M8 11V7a4 4 0 0 1 8 0v4"/>
        <circle cx="12" cy="16" r="1.5" fill="currentColor" stroke="none"/>
    </svg>;
}

/**
 * Mail icon (for the `email` field).
 */
export function IconMail() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5 shrink-0">
        <rect x="2" y="4" width="20" height="16" rx="2"/>
        <path d="M2 7l10 7 10-7"/>
    </svg>;
}
