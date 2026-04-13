from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import settings
from app.routers import auth, users, projects, tasks

app = FastAPI(
    title=settings.app_name,
    description="Kanban Board API with JWT authentication",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.on_event("startup")
async def startup_event():
    # Tables are created by Alembic migrations in production.
    # In development (DEBUG=true), auto-create for convenience.
    if settings.debug:
        from app.database import Base, engine
        from app.models import user, project, task  # noqa: F401
        Base.metadata.create_all(bind=engine)
