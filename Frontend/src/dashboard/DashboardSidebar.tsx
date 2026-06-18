export default function DashboardSidebar() {
    return (
        <div className="w-full max-w-md
                    bg-(--color-si-card-bg)
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300">
            <h1>Moje Organizacje</h1>
            <hr/>

            <h1>Moje Projekty</h1>
            <hr/>

            <h1>Moje Incydenty</h1>
            <hr/>
        </div>
    );
}