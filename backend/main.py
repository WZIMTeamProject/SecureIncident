import json
from pathlib import Path
from fastapi import FastAPI

BASE_DIR = Path(__file__).resolve().parent
OPENAPI_PATH = BASE_DIR.parent / "docs" / "api" / "openapi-core.json"

app = FastAPI(title="Secure Incident API")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    with open(OPENAPI_PATH, "r", encoding="utf-8") as f:
        openapi_schema = json.load(f)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

from api.routes import auth
app.include_router(auth.router, prefix="/api")


from api.routes import organization
app.include_router(organization.router, prefix="/api")


from api.routes import projects
app.include_router(projects.router, prefix="/api")