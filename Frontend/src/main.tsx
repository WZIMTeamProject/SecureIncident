import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import {createBrowserRouter} from 'react-router'
import {RouterProvider} from 'react-router/dom'
import './index.css'
import App from './App.tsx'
import SIStartPage from "./SIStartPage.tsx";
import SIDashboard from "./dashboard/SIDashboard.tsx";
import SILoginPage from "./login/SILoginPage.tsx";
import SIRegisterPage from "./login/SIRegisterPage.tsx";

const router = createBrowserRouter([
    {
        path: "/",
        Component: App,
        children: [
            {index: true, Component: SIStartPage},
            {path: "/dashboard", Component: SIDashboard},
            {path: "/login", Component: SILoginPage},
            {path: "/register", Component: SIRegisterPage}
        ]
    }
])

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <RouterProvider router={router}/>
    </StrictMode>,
)
