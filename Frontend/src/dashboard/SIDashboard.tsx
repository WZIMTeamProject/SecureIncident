import {Background} from "../components/Background.tsx";
import DashboardSidebar from "./DashboardSidebar.tsx";

export function SIDashboard() {
    return (
        <Background>
            <div className="flex flex-1 w-full gap-5">
                <DashboardSidebar/>

                <div>
                    TODO: Dashboard contents go here
                </div>
            </div>
        </Background>
    );
}