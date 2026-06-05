import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter, RouterContextProvider} from 'react-router'
import {RouterProvider} from 'react-router/dom'

import './index.css'

import {loggedUserLoader, SIAppRoot} from './SIAppRoot.tsx'

import {SIDashboard} from "./dashboard";
import {loginFormAction, loginMiddleware, SIForgotPassword, SILoginPage, SIRegisterPage} from "./login";
import {authGuardMiddleware, AuthRouterContext, getAuthState} from "./data/auth.ts";
import {SIStartPage} from "./SIStartPage.tsx";
import {SIPageNotFound} from "./SIPageNotFound.tsx";

const router = createBrowserRouter([
    {
        path: "/",
        Component: SIAppRoot,
        loader: loggedUserLoader,

        children: [
            {index: true, Component: SIStartPage},

            // Dashboards and other important stuff
            {path: "/dashboard", Component: SIDashboard, middleware: [authGuardMiddleware]},

            // Login related stuff
            {path: "/forgot_password", Component: SIForgotPassword},
            {path: "/login", Component: SILoginPage, middleware: [loginMiddleware], action: loginFormAction},
            {path: "/register", Component: SIRegisterPage},

            // Catch all 404 page for invalid routes
            {path: "*", Component: SIPageNotFound}
        ]
    }
], {
    getContext: async () => {
        const context = new RouterContextProvider();
        context.set(AuthRouterContext, await getAuthState());

        return context;
    }
});

if (import.meta.env.DEV) {
    console.log("DEV mode enabled.");
}

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router}/>
    </StrictMode>,
)
