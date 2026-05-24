export interface User {
    id: string,
    name: string
}

export function createDummyUser(): User {
    return {
        id: "0000-0000-0000-0000",
        name: "Debug User"
    }
}