from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings


app = FastAPI(
    title="Kanban DevOps API",
    version=settings.APP_VERSION,
    description="API base para el proyecto Kanban DevOps",
)


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


Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)