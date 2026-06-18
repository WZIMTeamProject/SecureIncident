import type {AuthState} from "./auth.ts";

export type SIContext = {
    auth?: AuthState,
    darkTheme?: boolean,
};