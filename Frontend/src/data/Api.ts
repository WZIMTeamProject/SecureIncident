import {AuthApi, Configuration, IncidentsApi, OrganizationApi, ProfilesApi, ProjectsApi} from "../api";

export default class Api {
    private static configuration: Configuration = new Configuration({
        basePath: "http://localhost:8000/api"
    });

    static auth: AuthApi = new AuthApi(Api.configuration);
    static incidents: IncidentsApi = new IncidentsApi(Api.configuration);
    static organization: OrganizationApi = new OrganizationApi(Api.configuration);
    static profiles: ProfilesApi = new ProfilesApi(Api.configuration);
    static projects: ProjectsApi = new ProjectsApi(Api.configuration);

    // add more API's from /api when needed
}