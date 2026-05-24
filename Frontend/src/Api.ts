import {AuthApi, Configuration} from "./api";

export default class Api {
    private static configuration: Configuration = new Configuration({
        basePath: "http://localhost:8000/api"
    })

    static auth: AuthApi = new AuthApi(Api.configuration);
    // add more API's from /api when needed
}