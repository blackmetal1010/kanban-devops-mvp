from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.routers.auth import router as auth_router
from app.routers.projects import router as projects_router
import app.models.user  # noqa: F401
import app.models.project  # noqa: F401
import app.models.project_member  # noqa: F401


app = FastAPI(
    title="Kanban DevOps API",
    version=settings.APP_VERSION,
    description="API base para el proyecto Kanban DevOps",
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "kanban-devops-mvp",
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.APP_ENV}


@app.get("/version")
def version() -> dict[str, str]:
    return {"version": settings.APP_VERSION}


app.include_router(auth_router)
app.include_router(projects_router)


Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False)
