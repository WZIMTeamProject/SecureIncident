import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter} from 'react-router'
import {RouterProvider} from 'react-router/dom'

import './index.css'

import App from './App.tsx'

import {dashboardMiddleware, SIDashboard} from "./dashboard";
import {loginAction, loginMiddleware, SIForgotPassword, SILoginPage, SIRegisterPage} from "./login";
import {SIPageNotFound, SIStartPage} from "./misc"

const router = createBrowserRouter([
    {
        path: "/",
        Component: App,

        children: [
            {index: true, Component: SIStartPage},

            // Dashboards and other important stuff
            {path: "/dashboard", Component: SIDashboard, middleware: [dashboardMiddleware]},

            // Login related stuff
            {path: "/forgot_password", Component: SIForgotPassword},
            {path: "/login", Component: SILoginPage, middleware: [loginMiddleware], action: loginAction},
            {path: "/register", Component: SIRegisterPage},

            // Catch all 404 page for invalid routes
            {path: "*", Component: SIPageNotFound}
        ]
    }
])

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router}/>
    </StrictMode>,
)
