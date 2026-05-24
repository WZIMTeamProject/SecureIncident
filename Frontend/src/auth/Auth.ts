import {createDummyUser, type User} from "./User.ts";
import Api from "../Api.ts";

export default class Auth {
    static debugMode: boolean = true

    private static dummyLogin: boolean = false

    static async getCurrentUser(): Promise<User | undefined> {
        if (this.debugMode) {
            if (this.dummyLogin) {
                return createDummyUser()
            } else {
                return undefined
            }
        }

        try {
            const {id, username} = await Api.auth.authMeGet()
            return {id: id, name: username}
        } catch {
            // TODO: specify what went wrong
            return undefined
        }
    }

    static async login(name: string, password: string, remember: boolean = false): Promise<User | undefined> {
        if (this.debugMode) {
            this.dummyLogin = true
            return createDummyUser()
        }

        try {
            const {id, username} = await Api.auth.authLoginPost({
                loginRequest: {username: name, password, rememberUser: remember}
            })

            return {id: id, name: username}
        } catch {
            // TODO: specify what went wrong
            return undefined
        }
    }

    static async logout(): Promise<boolean> {
        if (this.debugMode) {
            if (this.dummyLogin) {
                this.dummyLogin = false
                return true
            }

            return false
        }

        try {
            await Api.auth.authLogoutPost()
            return true
        } catch {
            // TODO: specify what went wrong
            return false
        }
    }
}