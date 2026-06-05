import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter} from 'react-router'
import {RouterProvider} from 'react-router/dom'

import './index.css'

import App from './App.tsx'

import {SIDashboard} from "./dashboard";
import {loginFormAction, loginMiddleware, SIForgotPassword, SILoginPage, SIRegisterPage} from "./login";
import {SIPageNotFound, SIStartPage} from "./misc"
import {authGuardMiddleware} from "./data/auth.ts";

const router = createBrowserRouter([
    {
        path: "/",
        Component: App,

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
])

if (import.meta.env.DEV) {
    console.log("DEV mode enabled.");
}

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router}/>
    </StrictMode>,
)
