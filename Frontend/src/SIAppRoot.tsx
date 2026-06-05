import {Link, type LoaderFunction, Outlet, type RouterContextProvider, useLoaderData} from "react-router";
import {AuthRouterContext, AuthState, AuthUserContext} from "./data/auth.ts";

export function SIAppRoot() {
    const authState = useLoaderData<AuthState | null>();

    return (
        <AuthUserContext value={authState}>
            <div className={`flex gap-2 p-2 bg-purple-600`}>
                {authState ? <LoggedUserToolbar/> : <AnonymousUserToolbar/>}
            </div>
            <div className={`flex justify-center`}>
                <Outlet/>
            </div>
        </AuthUserContext>
    )
}

export const loggedUserLoader: LoaderFunction = async ({context}) => {
    const middlewareContext = (context as Readonly<RouterContextProvider>);
    return middlewareContext.get(AuthRouterContext);
}

function AnonymousUserToolbar() {
    return <>
        <div><Link to={`/`}>Strona Główna</Link></div>
        <div><Link to={`/login`}>Logowanie</Link></div>
        <div><Link to={`/register`}>Rejestracja</Link></div>
    </>;
}

function LoggedUserToolbar() {
    return <>
        <div><Link to={`/`}>Strona Główna</Link></div>
        <div><Link to={`/dashboard`}>Dashboard</Link></div>
    </>;
}
