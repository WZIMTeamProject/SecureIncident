import {redirect} from "react-router";

export async function loadDashboard() {
    // TODO: implement dashboard when the DB gets implemented
    return redirect("/login")
}

export async function loadLoginPage() {
    // TODO: If the user is already authenticated, redirect to their dashboard instead
}