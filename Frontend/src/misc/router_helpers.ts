import type {Params, RouterContextProvider} from "react-router";

export type MiddlewareArgs = {
    request: Request;
    unstable_url: URL;
    unstable_pattern: string;
    params: Params;
    context: Readonly<RouterContextProvider>;
}

export type MiddlewareNext = {
    (): Promise<unknown>;
}