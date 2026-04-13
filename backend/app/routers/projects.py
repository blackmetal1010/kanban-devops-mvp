from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.dependencies import get_current_user


router = APIRouter(prefix="/api/projects", tags=["projects"])


def _get_owned_project_or_404(db: Session, project_id: int, owner_id: int) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == owner_id,
            Project.is_deleted.is_(False),
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = Project(
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        is_deleted=False,
    )
    db.add(project)
    db.flush()

    owner_membership = ProjectMember(project_id=project.id, user_id=current_user.id, role="OWNER")
    db.add(owner_membership)

    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectResponse]:
    projects = db.scalars(
        select(Project)
        .where(Project.owner_id == current_user.id, Project.is_deleted.is_(False))
        .order_by(Project.created_at.desc())
    ).all()
    return [ProjectResponse.model_validate(item) for item in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = _get_owned_project_or_404(db, project_id, current_user.id)
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = _get_owned_project_or_404(db, project_id, current_user.id)

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    project = _get_owned_project_or_404(db, project_id, current_user.id)
    project.is_deleted = True
    db.commit()
    return {"message": "Project deleted"}
