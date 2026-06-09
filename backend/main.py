import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

BASE_DIR = Path(__file__).resolve().parent
OPENAPI_PATH = BASE_DIR.parent / "docs" / "api" / "openapi-core.json"

app = FastAPI(title="Secure Incident API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


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

from api.routes import incidents

app.include_router(incidents.router, prefix="/api")

from api.routes import categories

app.include_router(categories.router, prefix="/api")

from api.routes import roles

app.include_router(roles.router, prefix="/api")

from api.routes import invitations

app.include_router(invitations.router, prefix="/api")

from api.routes import profiles

app.include_router(profiles.router, prefix="/api")

from api.routes import feedback

app.include_router(feedback.router, prefix="/api")

from api.routes import users

app.include_router(users.router, prefix="/api")
