import {Link, type LoaderFunction, Outlet, type RouterContextProvider, useLoaderData} from "react-router";
import {AuthRouterContext, AuthState, AuthUserContext} from "./data/auth.ts";
import {useState} from "react";

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
    const authState = useLoaderData<AuthState | null>();
    const [dark, setDark] = useState(false);


    const toggleDark = () => {
        setDark(d => !d);
        document.documentElement.classList.toggle("dark");
    };


    return (
        <AuthUserContext value={authState}>
            <header className="bg-[var(--color-si-header)] flex items-center px-4 py-3">

                {/* TODO: LOGO!!!! */}
                <div className="flex flex-col leading-tight mr-4">
                    <span className="text-base font-bold text-white">HELLO I'M THE LOGO</span>
                    <span className="text-base font-bold text-white">PLACEHOLDER</span>
                </div>

                {/* Two options for toolbar */}
                {authState ? <LoggedUserToolbar/> : <AnonymousUserToolbar/>}

                <div className="flex-1"/>

                {/* Mode switch */}
                <button
                    onClick={toggleDark}
                    title={dark ? "Tryb jasny" : "Tryb ciemny"}
                    className="p-2 rounded-lg text-white hover:bg-white/15 transition-colors"
                >
                    {dark ? <IconSun/> : <IconMoon/>}
                </button>

            </header>

            <Outlet/>
        </AuthUserContext>


    )
}

export const appRootLoader: LoaderFunction = async ({context}) => {
    const middlewareContext = (context as Readonly<RouterContextProvider>);
    return middlewareContext.get(AuthRouterContext);
}


function AnonymousUserToolbar() {
    return (
        <nav className="flex items-center gap-7 ml-2">
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
        <nav className="flex items-center">
            <NavIconLink to="/" label="Strona główna"><IconHome/></NavIconLink>
            <NavIconLink to="/account" label="Moje Konto"><IconUser/></NavIconLink>
            {/* TODO home icon, but only for users that have unlocked the dashboard (therefore completed their registration or simply logged in) */}
        </nav>
    );
}
