{/* Footer */}

// Shield icon
const Shield = ({ className }: { className?: string }) => (
    <svg viewBox="0 0 100 110" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
        <path d="M50 5 L90 22 L90 55 C90 78 72 98 50 105 C28 98 10 78 10 55 L10 22 Z"
            stroke="currentColor" strokeWidth="3" />
        <path d="M35 55 L46 66 L65 44" stroke="currentColor" strokeWidth="4"
            strokeLinecap="round" strokeLinejoin="round" />
    </svg>
);


export default function Footer() {
    return (
        <footer className="relative z-10 w-screen bg-(--color-si-footer) py-3 overflow-hidden">
            <div className="flex items-center gap-3 w-max mx-auto animate-none">
                {Array.from({ length: 40 }).map((_, i) => (
                    <Shield key={i} className="w-7 h-7 shrink-0 text-(--color-si-footer-shield) opacity-70" />
                ))}
            </div>
        </footer>
    );
}
