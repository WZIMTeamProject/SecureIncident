import {Link} from "react-router";
import {Background} from "./components/Background.tsx";

export function SIPageNotFound() {
    return (
    <Background>
        <div>

            <h1 className="text-(--color-si-join-us-text) text-left text-8xl font-bold ml-5">
            Hej!
            </h1>

            <h2 className="text-(--color-si-start-page-text) text-left text-4xl font-semibold mt-5 mb-5">
            Wygląda na to, że ta strona nie istnieje. <br></br>Przykro nam.
            </h2>

            <div className="text-(--color-si-start-page-text) text-center mt-7"  >
                <Link to="/" className="underline text-(--color-si-link) text-center hover:opacity-75 transition-opacity">Wróć na stronę główną</Link>
            </div>

    </div>
    </Background>

    );
}
