import {
    AuthApi,
    Configuration,
    IncidentsApi,
    OrganizationApi,
    ProfilesApi,
    ProjectsApi,
    RolesApi,
    UsersApi
} from "../api";

export default class Api {
    private static configuration: Configuration = new Configuration({
        basePath: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api", // This is important for CI/CD

        // Unfortunately, the backend currently only reads the token from the Authorization header in HTTP requests.
        // This makes it vulnerable to XSS, since I have to make the token readable through JS to be able to
        // manually paste it to each API request.
        accessToken: async (cookieName) => {
            if (!cookieName) { return ""; }
            return (await cookieStore.get(cookieName))?.value ?? "";
        }
    });

    static auth: AuthApi = new AuthApi(Api.configuration);
    static incidents: IncidentsApi = new IncidentsApi(Api.configuration);
    static organization: OrganizationApi = new OrganizationApi(Api.configuration);
    static profiles: ProfilesApi = new ProfilesApi(Api.configuration);
    static projects: ProjectsApi = new ProjectsApi(Api.configuration);
    static roles: RolesApi = new RolesApi(Api.configuration);
    static users: UsersApi = new UsersApi(Api.configuration);

    // add more API's from /api when needed
}
