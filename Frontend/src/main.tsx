import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter} from 'react-router'
import {RouterProvider} from 'react-router/dom'
import './index.css'
import {dashboardMiddleware, loginAction, loginMiddleware} from "./auth/middleware.ts";
import App from './App.tsx'
import SIStartPage from "./ui/SIStartPage.tsx";
import SIDashboard from "./ui/SIDashboard.tsx";
import SILoginPage from "./ui/SILoginPage.tsx";
import SIRegisterPage from "./ui/SIRegisterPage.tsx";
import SIPageNotFound from "./ui/SIPageNotFound.tsx";
import SIForgotPassword from "./ui/SIForgotPassword.tsx";

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
            {path: "*", Component: SIPageNotFound }
        ]
    }
])

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router}/>
    </StrictMode>,
)
