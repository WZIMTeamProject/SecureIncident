import {AuthUserContext} from "../data/auth.ts";
import {useContext, useEffect, useState} from "react";
import type {Organization} from "../data/project.ts";
import {LoadingMessage} from "../components/LoadingMessage.tsx";
import {OrganizationJoinOptions, ProjectList} from "./organization";

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
                    ? <OrganizationJoinOptions/>
                    : <ProjectList organization={organization}/>
            }
        </div>
    );
}
