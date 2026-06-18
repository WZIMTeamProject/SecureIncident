import {AuthUserContext} from "../data/auth.ts";
import {useContext, useEffect, useState} from "react";
import type {Organization} from "../data/project.ts";

export function SIOrganization() {
    const auth = useContext(AuthUserContext)!;

    const [organization, setOrganization] = useState<Organization | null>();

    useEffect(() => {
        auth.getOrganization().then((value) => {
            setOrganization(() => value);
        });
    }, [auth]);

    if (organization === undefined) {
        return <div><LoadingMessage/></div>;
    }

    return (
        <div>
            {
                organization === null
                    ? <CreateOrganizationWidget/>
                    : <OrganizationView organization={organization}/>
            }
        </div>
    );
}

function LoadingMessage() {
    return <h1>Wczytywanie...</h1>;
}

function CreateOrganizationWidget() {
    return <div>TODO dodaj organizację dla tych co nie mają</div>;
}

function OrganizationView({organization}: { organization: Organization }) {
    return (
        <div>
            <div className="p-3">
                <h1 className="text-2xl font-bold">{organization.name}</h1>
                <p className="text-md text-gray-600 italic font-normal">{organization.description ?? "Brak opisu"}</p>
            </div>

            <div className="w-full h-96
                    border-5 border-(--color-si-card-border)
                    rounded-2xl shadow-lg px-8 py-8 transition-colors duration-300 overflow-y-scroll">
                <p>TODO projekty</p>
            </div>

            <div className="w-full flex gap-3 p-3 justify-end">
                <button className="px-6 py-2
                        bg-[var(--color-si-btn)]
                        hover:bg-[var(--color-si-btn-hover)] shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj nowy projekt
                </button>

                <button className="px-6 py-2
                        bg-[var(--color-si-btn)]
                        hover:bg-[var(--color-si-btn-hover)] shadow-lg
                        text-white text-md font-semibold rounded-lg cursor-pointer transition-colors duration-200">
                    Dodaj użytkownika do organizacji
                </button>
            </div>

            <div className="w-full flex px-3 justify-end">
                <button className="px-6 py-2
                        bg-[var(--color-si-btn-error)]
                        hover:bg-[var(--color-si-btn-error-hover)] shadow-lg
                        text-white text-md font-semibold underline rounded-lg cursor-pointer transition-colors duration-200">
                    Usuń organizację
                </button>
            </div>
        </div>
    );
}