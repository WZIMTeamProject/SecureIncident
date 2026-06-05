import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter, RouterContextProvider} from 'react-router'
import {RouterProvider} from 'react-router/dom'

import './index.css'

import {appRootLoader, SIAppRoot} from './SIAppRoot.tsx'

import {SIDashboard} from "./dashboard";
import {loginFormAction, loginMiddleware, SIForgotPassword, SILoginPage, SIRegisterPage} from "./login";
import {AuthRouterContext, authUserLoader, getAuthState} from "./data/auth.ts";
import {SIStartPage} from "./SIStartPage.tsx";
import {SIPageNotFound} from "./SIPageNotFound.tsx";
import {SIAccountPage, SINotificationPage} from "./account";

const router = createBrowserRouter([
    {
        path: "/",
        Component: SIAppRoot,
        loader: appRootLoader,

        children: [
            {index: true, Component: SIStartPage},

            // Dashboards and other important stuff
            {path: "/dashboard", Component: SIDashboard, loader: authUserLoader},

            // Login related stuff
            {
                path: "/login",
                children: [
                    {index: true, Component: SILoginPage, middleware: [loginMiddleware], action: loginFormAction},
                    {path: "/login/forgot_password", Component: SIForgotPassword},
                    {path: "/login/register", Component: SIRegisterPage}
                ]
            },

            // Account related stuff
            {
                path: "/account",
                children: [
                    {index: true, Component: SIAccountPage, loader: authUserLoader},
                    {path: "/account/notifications", Component: SINotificationPage, loader: authUserLoader}
                ]
            },

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
