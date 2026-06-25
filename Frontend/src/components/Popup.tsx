import * as React from "react";

export function Popup({show, children, className}: { show: boolean, children?: React.ReactNode, className?: string }) {
    return (
        <div
            hidden={!show}
            className={`fixed top-0 left-0 w-full h-full
                bg-black/30
                flex justify-center items-center`}>

            <div className={`bg-(--color-si-card-bg)
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300 ${className}`}>
                {show && (children ?? <PointAndLaughAtTheDeveloper/>)}
            </div>
        </div>
    );
}

function PointAndLaughAtTheDeveloper() {
    return <h1 className="text-2xl font-bold text-black">
        Jeżeli to czytasz, to znaczy że zapomniałeś/aś dodać opcji zamknięcia popupu ;)
    </h1>;
}
