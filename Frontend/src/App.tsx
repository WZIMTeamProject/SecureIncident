import './App.css'
import {Outlet} from "react-router";
import {SIToolbar} from "./SIToolbar.tsx";

function App() {
    return (
        <>
            <SIToolbar/>
            <div>
                <Outlet />
            </div>
        </>
    )
}

export default App
