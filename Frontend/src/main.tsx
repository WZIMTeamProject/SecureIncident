import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter, type LoaderFunction, RouterContextProvider} from 'react-router'
import {RouterProvider} from 'react-router/dom'

import './index.css'

import {SIAppRoot} from './SIAppRoot.tsx'

import {SIDashboard, SIProject} from "./dashboard";
import {
    forgotPasswordAction,
    loginFormAction,
    logoutMiddleware,
    redirectToDashboardMiddleware,
    registerFormAction, resetPasswordAction,
    SIForgotPassword,
    SILoginPage,
    SIRegisterPage
} from "./login";
import {AuthRouterContext, authUserLoader, getAuthState} from "./data/auth.ts";
import {SIStartPage} from "./SIStartPage.tsx";
import {SIPageNotFound} from "./SIPageNotFound.tsx";
import {SIAccountPage, SINotificationPage} from "./account";
import {SIResetPassword} from "./login/SIResetPassword.tsx";
import {THEME_PREFERENCE, THEME_PREFERENCE_DARK} from "./data/cookies.ts";
import type {SIContext} from "./data/context.ts";
import {SIOrganization} from "./dashboard/SIOrganization.tsx";
import {SIIncident} from "./dashboard/SIIncident.tsx";

const appRootLoader: LoaderFunction = async ({context}) => {
    const middlewareContext = (context as Readonly<RouterContextProvider>);

    const wantsDarkMode = await cookieStore.get(THEME_PREFERENCE);

    const siContext: SIContext = {
        auth: middlewareContext.get(AuthRouterContext) ?? undefined,
        darkTheme: wantsDarkMode?.value == THEME_PREFERENCE_DARK
    };

    return siContext;
}

const router = createBrowserRouter([
    {
        path: "/",
        Component: SIAppRoot,
        loader: appRootLoader,

        children: [
            {index: true, Component: SIStartPage},

            // Dashboards and other important stuff
            {
                path: "/dashboard",
                Component: SIDashboard,
                loader: authUserLoader,
                children: [
                    {
                        index: true,
                        Component: SIOrganization,
                    },
                    {
                        path: "/dashboard/project/:projectId",
                        Component: SIProject,
                    },
                    {
                        path: "/dashboard/incident/:incidentId",
                        Component: SIIncident,
                    }
                ]
            },

            // Login related stuff
            {
                path: "/login",
                children: [
                    {
                        index: true,
                        Component: SILoginPage,
                        middleware: [logoutMiddleware, redirectToDashboardMiddleware],
                        action: loginFormAction
                    },
                    {
                        path: "/login/forgot_password",
                        Component: SIForgotPassword,
                        middleware: [redirectToDashboardMiddleware],
                        action: forgotPasswordAction
                    },
                    {
                        path: "/login/register",
                        Component: SIRegisterPage,
                        middleware: [redirectToDashboardMiddleware],
                        action: registerFormAction
                    }
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

            // Reset password page (link gets sent via email)
            {
                path: "/reset-password",
                Component: SIResetPassword,
                action: resetPasswordAction,
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
