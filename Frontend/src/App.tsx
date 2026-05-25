import {Outlet} from "react-router";

import {SIToolbar} from "./misc";

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
