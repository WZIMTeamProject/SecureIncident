import './App.css'
import {Outlet} from "react-router";
import SIToolbar from "./ui/SIToolbar.tsx";

function App() {
    return (
        <>
            <SIToolbar/>
            <div className={`flex justify-center`}>
                <Outlet/>
            </div>
        </>
    )
}

export default App
