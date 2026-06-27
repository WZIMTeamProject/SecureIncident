export function AppLogo() {
    return <svg viewBox="0 0 144 60" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg" x1="24" y1="24" x2="56" y2="68" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#6d28d9"/>
                <stop offset="42%" stop-color="#2563eb"/>
                <stop offset="100%" stop-color="#06b6d4"/>
            </linearGradient>
            <linearGradient id="sh" x1="26" y1="26" x2="46" y2="50" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="white" stop-opacity="0.35"/>
                <stop offset="100%" stop-color="white" stop-opacity="0"/>
            </linearGradient>
            <linearGradient id="gl" x1="40" y1="48" x2="40" y2="60" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="white" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="white" stop-opacity="0"/>
            </linearGradient>
            <radialGradient id="hl" cx="50%" cy="55%" r="50%">
                <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.9"/>
                <stop offset="40%" stop-color="#2563eb" stop-opacity="0.55"/>
                <stop offset="75%" stop-color="#6d28d9" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#6d28d9" stop-opacity="0"/>
            </radialGradient>
            <filter id="gf" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="2.5" result="b"/>
                <feMerge>
                    <feMergeNode in="b"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <g transform="translate(8, 1) scale(0.58)">
            <ellipse cx="40" cy="50" rx="44" ry="42" fill="url(#hl)"/>
            <g filter="url(#gf)">
                <path d="M40 4 L74 20 L74 48 Q74 74 40 88 Q6 74 6 48 L6 20 Z" fill="url(#bg)"/>
                <path d="M40 10 L70 24 L70 38 Q58 26 40 22 Q22 26 10 38 L10 24 Z" fill="url(#sh)"/>
                <path d="M40 14 L68 27 L68 48 Q68 68 40 80 Q12 68 12 48 L12 27 Z" stroke="white" stroke-width="1.4" stroke-opacity="0.25" fill="none"/>
                <path d="M20 35 L20 45 L30 45" stroke="white" stroke-width="1.2" stroke-opacity="0.22" stroke-linecap="round" fill="none"/>
                <circle cx="20" cy="35" r="2" fill="white" fill-opacity="0.28"/>
                <circle cx="30" cy="45" r="1.5" fill="white" fill-opacity="0.2"/>
                <path d="M60 35 L60 45 L50 45" stroke="white" stroke-width="1.2" stroke-opacity="0.22" stroke-linecap="round" fill="none"/>
                <circle cx="60" cy="35" r="2" fill="white" fill-opacity="0.28"/>
                <circle cx="50" cy="45" r="1.5" fill="white" fill-opacity="0.2"/>
                <path d="M20 70 L30 70 L30 60" stroke="white" stroke-width="1.2" stroke-opacity="0.18" stroke-linecap="round" fill="none"/>
                <circle cx="20" cy="70" r="2" fill="white" fill-opacity="0.2"/>
                <circle cx="30" cy="60" r="1.5" fill="white" fill-opacity="0.18"/>
                <path d="M60 70 L50 70 L50 60" stroke="white" stroke-width="1.2" stroke-opacity="0.18" stroke-linecap="round" fill="none"/>
                <circle cx="60" cy="70" r="2" fill="white" fill-opacity="0.2"/>
                <circle cx="50" cy="60" r="1.5" fill="white" fill-opacity="0.18"/>
                <path d="M31 52 L31 38 Q31 26 40 26 Q49 26 49 38 L49 52" stroke="white" stroke-width="5.6" stroke-linecap="round" fill="none"/>
                <path d="M34 52 L34 39 Q34 29 40 29 Q46 29 46 39 L46 52" stroke="white" stroke-width="1.8" stroke-opacity="0.3" stroke-linecap="round" fill="none"/>
                <rect x="25" y="50" width="30" height="26" rx="5" fill="white" opacity="0.92"/>
                <rect x="25" y="50" width="30" height="11" rx="5" fill="url(#gl)"/>
                <rect x="25" y="50" width="30" height="26" rx="5" stroke="white" stroke-width="1" stroke-opacity="0.4" fill="none"/>
                <rect x="35" y="63" width="10" height="4" rx="2" fill="#2563eb" opacity="0.5"/>
            </g>
        </g>

        <text x="62" y="31" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="800" fill="#ffffff" letter-spacing="-0.5">Secure</text>
        <text x="62" y="46" font-family="Inter, Arial, sans-serif" font-size="13" font-weight="700" fill="#e9d5ff" letter-spacing="1.5">INCI</text>

        <g transform="translate(96, 37.4) scale(0.8)">
            <path d="M2 6 L2 3 Q2 0 5 0 Q8 0 8 3 L8 6" stroke="#e9d5ff" stroke-width="1.9" stroke-linecap="round" fill="none"/>
            <rect x="1" y="4.1" width="8" height="7" rx="1.5" fill="#e9d5ff"/>
            <circle cx="5" cy="8" r="1.2" fill="#5a1b8a" opacity="0.7"/>
        </g>

        <text x="106" y="46" font-family="Inter, Arial, sans-serif" font-size="13" font-weight="700" fill="#e9d5ff" letter-spacing="1.5">ENT</text>
    </svg>;
}

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
 * Monitor/screen icon (for the Dashboard navigation link).
 */
export function IconDashboard() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0" aria-hidden="true">
        <rect x="2" y="3" width="20" height="14" rx="2"/>
        <line x1="12" y1="17" x2="12" y2="21"/>
        <line x1="8" y1="21" x2="16" y2="21"/>
    </svg>;
}

/**
 * Door with exit arrow icon (for the logout action).
 */
export function IconLogout() {
    return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round"
                strokeLinejoin="round" className="w-5 h-5 shrink-0" aria-hidden="true">
        <path d="M9 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h4"/>
        <line x1="15" y1="12" x2="21" y2="12"/>
        <polyline points="18 9 21 12 18 15"/>
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
