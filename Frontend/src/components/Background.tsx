import type { ReactNode } from "react";
import Footer from "../components/Footer.tsx"; 

// Shield icon
const Shield = ({ className }: { className?: string }) => (
    <svg viewBox="0 0 100 110" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
        <path d="M50 5 L90 22 L90 55 C90 78 72 98 50 105 C28 98 10 78 10 55 L10 22 Z"
            stroke="currentColor" strokeWidth="3" />
        <path d="M35 55 L46 66 L65 44" stroke="currentColor" strokeWidth="4"
            strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);

interface PageBgProps {
    children: ReactNode;
    className?: string;
}

export function Background({ children, className = "" }: PageBgProps) {
    return (
        <div className={`min-h-screen flex flex-col bg-(--color-si-page-bg) transition-colors duration-300 ${className}`}>
            {/* Background shield icons */}
            <div className="pointer-events-none select-none fixed inset-0 z-0 overflow-hidden">
                <Shield className="absolute left-6 top-40 w-92 h-92 text-(--color-si-shield) opacity-10" />
                <Shield className="absolute left-1/2 top-20 w-52 h-52 text-(--color-si-shield) opacity-10 mt-5" />
                <Shield className="absolute right-6 bottom-20 w-72 h-72 text-(--color-si-shield) opacity-15" />
            </div>

            {/* Rest of the page*/}
            <div className="relative z-10 flex flex-col flex-1 items-center justify-center gap-4 py-12 px-4">
                {children}
            </div>

            {/* Footer */}
            <Footer />

        </div>
    );
}
