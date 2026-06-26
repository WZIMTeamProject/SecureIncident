export function LoadingMessage({message, className}: {message?: string, className?: string}) {
    return (
        <div className={`p-3 ${className}`}>
            <h1 className="text-2xl font-bold text-(--color-si-label)">
                {message ?? "Wczytywanie..."}
            </h1>
        </div>
    );
}
