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

    return (
        <div>
            {
                organization === undefined
                    ? <LoadingMessage/>
                    : organization === null
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
    return <div>
        <h1>{organization.name} ({organization.id})</h1>
        <h3>Opis: {organization.description ?? "brak opisu"}</h3>
    </div>
}