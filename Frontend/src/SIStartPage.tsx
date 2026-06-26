import {Background} from "./components/Background.tsx";
import {Link} from "react-router";
import bgLockLight from "./components/images/Secure Incident lock bright.png";
import bgLockDark from "./components/images/Secure Incident lock dark.png";


export function SIStartPage() {

    return (
    <Background>

            <div className="w-full flex flex-col items-center ">

                <section className="relative mt-3 w-screen mx-[calc(50%-50vw)] aspect-[1920/658] min-h-44 max-h-[420px] lg:max-h-[520px]">
                    <img
                        src={bgLockLight}
                        alt=""
                        aria-hidden="true"
                        className="block dark:hidden w-full h-full object-cover"
                    />
                    <img
                        src={bgLockDark}
                        alt=""
                        aria-hidden="true"
                        className="hidden dark:block w-full h-full object-cover"
                    />

                    <div className="absolute inset-0 flex items-center">
                        <div className="px-6 md:px-16 max-w-xl">
                            <h1 className="text-white text-2xl md:text-3xl ml-10 font-bold leading-snug drop-shadow-md">
                                Twój zaufany manager <br></br> incydentów
                            </h1>
                            <span className="block w-50 h-0.5 bg-white/70 mt-6 ml-23"/>
                        </div>
                    </div>
                </section>

                {/* About us section */}
                <section className="w-full max-w-3xl px-6 py-10 text-center md:text-left">
                    <p className="text-(--color-si-start-page-text) font-bold leading-relaxed mb-4">
                        Jesteśmy webową platformą dla małych organizacji do zgłaszania, przypisywania
                        i śledzenia problemów oraz incydentów w obrębie projektów, z naciskiem na role,
                        bezpieczeństwo, historię zmian i czytelny workflow.
                    </p>
                    <p className="text-(--color-si-start-page-text) leading-relaxed mb-4">
                        Wiemy, że w niewielkich organizacjach zgłoszenia problemów często giną
                        w komunikatorach, mailach lub ustnych ustaleniach. Trudno potem ustalić,
                        kto zgłosił problem, kto odpowiada za jego rozwiązanie, na jakim etapie
                        jest sprawa, jakie działania już wykonano, i tym podobne.
                    </p>
                    <p className="text-(--color-si-start-page-text) font-bold leading-relaxed">
                        Mamy nadzieję, że korzystanie z SecureIncident sprawi Twojej organizacji
                        samą przyjemność!
                    </p>
                </section>

                {/* Links */}
                <section className="w-full flex flex-col items-center gap-2 pb-12">
                    <h2 className="text-(--color-si-join-us-text) text-4xl font-bold mt-7 mb-5">Dołącz do nas!</h2>
                    <Link to="/login/register"
                          className="underline text-(--color-si-link) hover:opacity-75 transition-opacity">
                        Zarejestruj się
                    </Link>
                    <Link to="/login"
                          className="underline text-(--color-si-link) hover:opacity-75 transition-opacity">
                        Mam już konto
                    </Link>
                </section>

            </div>
    </Background>

    );
}
