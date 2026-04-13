from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberResponse,
    ProjectMemberUpsertRequest,
    ProjectResponse,
    ProjectStatsResponse,
    ProjectRole,
    ProjectUpdate,
)
from app.schemas.task import TaskStatus
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


def _get_project_for_user_or_404(db: Session, project_id: int, user_id: int) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.is_deleted.is_(False),
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.owner_id == user_id:
        return project

    membership = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project


def _membership_to_response(item: ProjectMember) -> ProjectMemberResponse:
    return ProjectMemberResponse(
        project_id=item.project_id,
        user_id=item.user_id,
        role=ProjectRole(item.role),
    )


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


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def upsert_project_member(
    project_id: int,
    payload: ProjectMemberUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectMemberResponse:
    project = _get_owned_project_or_404(db, project_id, current_user.id)

    target_user = db.get(User, payload.user_id)
    if target_user is None or not target_user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    role_value = ProjectRole.OWNER.value if payload.user_id == project.owner_id else payload.role.value

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == payload.user_id,
        )
    )

    if member is None:
        member = ProjectMember(project_id=project_id, user_id=payload.user_id, role=role_value)
        db.add(member)
    else:
        member.role = role_value

    db.commit()
    db.refresh(member)
    return _membership_to_response(member)


@router.get("/{project_id}/members", response_model=list[ProjectMemberResponse])
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectMemberResponse]:
    _get_owned_project_or_404(db, project_id, current_user.id)
    members = db.scalars(
        select(ProjectMember)
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.id.asc())
    ).all()
    return [_membership_to_response(item) for item in members]


@router.get("/{project_id}/stats", response_model=ProjectStatsResponse)
def get_project_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectStatsResponse:
    _get_project_for_user_or_404(db, project_id, current_user.id)

    statuses = db.scalars(
        select(Task.status).where(
            Task.project_id == project_id,
            Task.is_deleted.is_(False),
        )
    ).all()

    counts = Counter(statuses)
    total = len(statuses)
    done = counts.get(TaskStatus.DONE.value, 0)
    pct_complete = round((done / total) * 100, 2) if total else 0.0

    return ProjectStatsResponse(
        project_id=project_id,
        total=total,
        todo=counts.get(TaskStatus.TODO.value, 0),
        in_progress=counts.get(TaskStatus.IN_PROGRESS.value, 0),
        done=done,
        pct_complete=pct_complete,
    )
