import logging.config
import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from alembic.config import Config
from alembic import command

from core.config import settings
from middleware.logging_middleware import LoggingMiddleware

BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)

_formatter = "json" if settings.LOG_FORMAT == "json" else "default"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "middleware.logging_middleware.RequestIDFilter",
        },
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": _formatter,
            "filters": ["request_id"],
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "backend": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)


def run_migrations():
    os.environ["DATABASE_URL"] = settings.DATABASE_URL
    alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running database migrations...")
    try:
        await asyncio.to_thread(run_migrations)
        logger.info("Database migrations completed successfully.")
    except Exception as e:
        logger.exception("Database migration failed")
        raise
    yield


app = FastAPI(
    title="Secure Incident API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)  # Added LAST = outermost = sees all requests including CORS preflight

err_logger = logging.getLogger("backend.errors")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    err_logger.warning(
        "HTTP %s at %s %s",
        exc.status_code,
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    err_logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}



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

from api.routes import users
app.include_router(users.router, prefix="/api")
