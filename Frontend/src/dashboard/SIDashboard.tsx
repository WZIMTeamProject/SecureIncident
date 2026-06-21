import {Background} from "../components/Background.tsx";
import DashboardSidebar from "./DashboardSidebar.tsx";
import {Outlet} from "react-router";

export function SIDashboard() {
    return (
        <Background>
            <div className="flex flex-1 w-full gap-5">
               <DashboardSidebar/>

                <div className="w-full px-8 py-8 transition-colors duration-300">
                    <Outlet/>
                </div>
            </div>
        </Background>
    );
}