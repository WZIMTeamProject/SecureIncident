import {type ActionFunction} from "react-router";
import {
    FORM_ACTION,
    FORM_ACTION_DELETE_ORGANIZATION,
    FORM_ACTION_INVITE_USER,
    FORM_ACTION_NEW_PROJECT, FORM_PROJECT_DESCRIPTION, FORM_PROJECT_NAME
} from "./forms.ts";
import Api from "../data/Api.ts";

export const dashboardOrganizationAction: ActionFunction = async ({request}) => {
    const formData = await request.formData();

    const organizationAction = formData.get(FORM_ACTION)?.toString();
    if (!organizationAction) {
        return { ok: false };
    }

    if (request.method === "POST") {
        if (organizationAction === FORM_ACTION_NEW_PROJECT) {
            const projectName = formData.get(FORM_PROJECT_NAME)?.toString()?.trim();
            const projectDescription = formData.get(FORM_PROJECT_DESCRIPTION)?.toString()?.trim();

            if (projectName) {
                const createdId = await Api.projects.projectsPost({
                    createProjectRequest: {
                        name: projectName,
                        description: projectDescription,
                        scope: "ORGANIZATION"
                    }
                }).catch(() => null);

                if (createdId) {
                    return { ok: true };
                }
            }
        } else if (organizationAction === FORM_ACTION_INVITE_USER) {
            // TODO
            return { ok: true }
        }
    } else if (request.method === "DELETE") {
        if (organizationAction === FORM_ACTION_DELETE_ORGANIZATION) {
            // TODO
            return { ok: true }
        }
    }

    return { ok: false };
};