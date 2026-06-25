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

/**
 * ID card icon (for the `first name` field).
 */
export function IconIdCard() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <circle cx="8.5" cy="11" r="2"/>
        <path d="M5.5 16c0.4-1.5 1.6-2.3 3-2.3s2.6 0.8 3 2.3"/>
        <line x1="14" y1="10.5" x2="18" y2="10.5"/>
        <line x1="14" y1="14" x2="17" y2="14"/>
    </svg>;
}

/**
 * Tag icon (for the `last name` field).
 */
export function IconTag() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <path d="M4 4h7l9 9-7 7-9-9V4z"/>
        <circle cx="8" cy="8" r="1.5"/>
    </svg>;
}

/**
 * Lock with a checkmark icon (for the `repeat password` field).
 */
export function IconLockCheck() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <rect x="5" y="11" width="14" height="10" rx="2"/>
        <path d="M8 11V7a4 4 0 0 1 8 0v4"/>
        <path d="M9.5 16l1.7 1.7L15 14.5"/>
    </svg>;
}

/**
 * Image/picture icon (for the `profile picture URL` field).
 */
export function IconImage() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <rect x="3" y="5" width="18" height="14" rx="2"/>
        <circle cx="8.5" cy="10" r="1.5"/>
        <path d="M21 16l-5-5L5 19"/>
    </svg>;
}

/**
 * Comment/chat bubble icon (for `COMMENT` notifications).
 */
export function IconComment() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0">
        <path d="M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9l-5 4V6a1 1 0 0 1 1-1z"/>
        <line x1="8" y1="10" x2="16" y2="10"/>
        <line x1="8" y1="13" x2="13" y2="13"/>
    </svg>;
}

/**
 * Hamburger icon (opens the mobile navigation menu).
 */
export function IconMenu() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round"
                className="w-5 h-5 shrink-0">
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>;
}

/**
 * Close icon (closes the mobile navigation menu).
 */
export function IconClose() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round"
                className="w-5 h-5 shrink-0">
        <line x1="6" y1="6" x2="18" y2="18"/>
        <line x1="6" y1="18" x2="18" y2="6"/>
    </svg>;
}

export function IconClipboard() {
    return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 shrink-0">
        <path
            d="M7 4V2H17V4H20.0066C20.5552 4 21 4.44495 21 4.9934V21.0066C21 21.5552 20.5551 22 20.0066 22H3.9934C3.44476 22 3 21.5551 3 21.0066V4.9934C3 4.44476 3.44495 4 3.9934 4H7ZM7 6H5V20H19V6H17V8H7V6ZM9 4V6H15V4H9Z"></path>
    </svg>;
}

export function IconCheck() {
    return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 shrink-0">
        <path
            d="M9.9997 15.1709L19.1921 5.97852L20.6063 7.39273L9.9997 17.9993L3.63574 11.6354L5.04996 10.2212L9.9997 15.1709Z"></path>
    </svg>;
}