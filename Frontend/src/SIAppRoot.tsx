import {Link, Outlet, useLoaderData} from "react-router";
import {AuthState, AuthUserContext} from "./data/auth.ts";
import {useEffect, useState} from "react";
import {AppLogo, IconClose, IconMenu} from "./components/icons.tsx";
import {THEME_PREFERENCE, THEME_PREFERENCE_DARK, THEME_PREFERENCE_LIGHT} from "./data/cookies.ts";
import type {SIContext} from "./data/context.ts";

// TODO: LOGO!!!!!

// Header icons

const IconSun = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-5 h-5">
        <circle cx="12" cy="12" r="4"/>
        {[0, 45, 90, 135, 180, 225, 270, 315].map(deg => (
            <line key={deg}
                  x1={12 + 7 * Math.cos(deg * Math.PI / 180)}
                  y1={12 + 7 * Math.sin(deg * Math.PI / 180)}
                  x2={12 + 9.5 * Math.cos(deg * Math.PI / 180)}
                  y2={12 + 9.5 * Math.sin(deg * Math.PI / 180)}
            />
        ))}
    </svg>
);

const IconMoon = () => (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
);

const IconUser = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5">
        <circle cx="12" cy="8" r="4"/>
        <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/>
    </svg>
);

const IconHome = () => (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} className="w-5 h-5">
        <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/>
        <path d="M9 21V12h6v9"/>
    </svg>
);

// Helpers

const NavLink = ({to, children}: { to: string; children: React.ReactNode }) => (
    <Link to={to} className="px-3 py-1.5 rounded-lg text-white text-sm font-medium hover:bg-white/15 transition-colors">
        {children}
    </Link>
);

const NavIconLink = ({to, label, children}: { to: string; label: string; children: React.ReactNode }) => (
    <Link to={to} title={label} className="p-2 rounded-lg text-white hover:bg-white/15 transition-colors">
        {children}
    </Link>
);


export function SIAppRoot() {
    const siContext = useLoaderData<SIContext>();

    const [dark, setDark] = useState(siContext.darkTheme);
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        if (dark) {
            cookieStore.set(THEME_PREFERENCE, THEME_PREFERENCE_DARK).then(() => {
                console.log("Set theme to: dark");
            });
        } else {
            cookieStore.set(THEME_PREFERENCE, THEME_PREFERENCE_LIGHT).then(() => {
                console.log("Set theme to: light");
            });
        }
    }, [dark]);

    return (
        <div className={dark ? "dark" : ""}>
            <AuthUserContext value={siContext.auth ?? null}>
                <header className="bg-(--color-si-header)">
                    <div className="flex items-center">
                        <div className="min-h-full min-w-36 leading-tight ml-4">
                            <AppLogo/>
                        </div>

                        <div className="flex items-center px-4 py-3 w-full">
                            {/* Desktop toolbar — collapses into the mobile menu below md */}
                            {siContext.auth ? <LoggedUserToolbar/> : <AnonymousUserToolbar/>}

                            <div className="flex-1"/>

                            {/* Mode switch */}
                            <button
                                onClick={() => setDark(!dark)}
                                title={dark ? "Tryb jasny" : "Tryb ciemny"}
                                className="p-2 rounded-lg text-white hover:bg-white/15 transition-colors hover:cursor-pointer"
                            >
                                {dark ? <IconSun/> : <IconMoon/>}
                            </button>

                            {/* Hamburger — only below md */}
                            <button
                                onClick={() => setMenuOpen(!menuOpen)}
                                aria-label={menuOpen ? "Zamknij menu" : "Otwórz menu"}
                                aria-expanded={menuOpen}
                                aria-controls="mobile-menu"
                                className="md:hidden flex items-center justify-center min-h-11 min-w-11 ml-1 rounded-lg text-white hover:bg-white/15 transition-colors"
                            >
                                {menuOpen ? <IconClose/> : <IconMenu/>}
                            </button>

                        </div>
                    </div>

                    {menuOpen && <MobileNav authState={siContext.auth ?? null} onNavigate={() => setMenuOpen(false)}/>}

                </header>

                <Outlet/>
            </AuthUserContext>
        </div>
    )
}

function AnonymousUserToolbar() {
    return (
        <nav className="hidden md:flex items-center gap-7 ml-2">
            <NavLink to="/">Strona główna</NavLink>
            <span className="text-white/50">|</span>
            <NavLink to="/login">Logowanie</NavLink>
            <span className="text-white/50">|</span>
            <NavLink to="/login/register">Rejestracja</NavLink>
        </nav>
    );
}

function LoggedUserToolbar() {
    return (
        <nav className="hidden md:flex items-center">
            <NavIconLink to="/" label="Strona główna"><IconHome/></NavIconLink>
            <NavIconLink to="/account" label="Moje Konto"><IconUser/></NavIconLink>
            <NavIconLink to="/dashboard" label="Dashboard">DASHBOARD TEMP</NavIconLink>
            <NavIconLink to="/login?logout=true" label="Wyloguj">LOGOUT TEMP</NavIconLink>
            {/* TODO Ikonki do dashboardu i wylogowywanie (pamiętać też o MobileNav poniżej) */}
        </nav>
    );
}

function MobileNav({authState, onNavigate}: { authState: AuthState | null; onNavigate: () => void }) {
    const linkClass = "flex items-center justify-center gap-3 px-4 py-3 text-white text-base font-medium hover:bg-white/15 transition-colors";
    return (
        <nav id="mobile-menu" aria-label="Nawigacja mobilna"
             className="md:hidden flex flex-col border-t border-white/15 pb-2">
            {authState ? (
                <>
                    <Link to="/" onClick={onNavigate} className={linkClass}><IconHome/>Strona główna</Link>
                    <Link to="/account" onClick={onNavigate} className={linkClass}><IconUser/>Moje Konto</Link>
                    <Link to="/dashboard" onClick={onNavigate} className={linkClass}>Dashboard</Link>
                    <Link to="/login?logout=true" onClick={onNavigate} className={linkClass}>Wyloguj</Link>
                </>
            ) : (
                <>
                    <Link to="/" onClick={onNavigate} className={linkClass}>Strona główna</Link>
                    <Link to="/login" onClick={onNavigate} className={linkClass}>Logowanie</Link>
                    <Link to="/login/register" onClick={onNavigate} className={linkClass}>Rejestracja</Link>
                </>
            )}
        </nav>
    );
}
