from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from app.services.dependencies import get_current_user


router = APIRouter(prefix="/api/projects/{project_id}/tasks", tags=["tasks"])


def _get_project_for_user(db: Session, project_id: int, user_id: int) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.is_deleted.is_(False),
            or_(
                Project.owner_id == user_id,
                select(ProjectMember.id)
                .where(
                    and_(
                        ProjectMember.project_id == project_id,
                        ProjectMember.user_id == user_id,
                    )
                )
                .exists(),
            ),
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _get_task_or_404(db: Session, project_id: int, task_id: int) -> Task:
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id,
            Task.is_deleted.is_(False),
        )
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _validate_status_transition(current_status: str, new_status: str) -> None:
    if current_status == new_status:
        return
    allowed = {
        (TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value),
        (TaskStatus.IN_PROGRESS.value, TaskStatus.DONE.value),
        (TaskStatus.DONE.value, TaskStatus.IN_PROGRESS.value),
    }
    if (current_status, new_status) not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current_status} -> {new_status}",
        )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    _get_project_for_user(db, project_id, current_user.id)

    if payload.assigned_to is not None and db.get(User, payload.assigned_to) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status=TaskStatus.TODO.value,
        assigned_to=payload.assigned_to,
        created_by=current_user.id,
        is_deleted=False,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TaskResponse]:
    _get_project_for_user(db, project_id, current_user.id)
    tasks = db.scalars(
        select(Task)
        .where(
            Task.project_id == project_id,
            Task.is_deleted.is_(False),
        )
        .order_by(Task.created_at.asc())
    ).all()
    return [TaskResponse.model_validate(item) for item in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    _get_project_for_user(db, project_id, current_user.id)
    task = _get_task_or_404(db, project_id, task_id)
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    project_id: int,
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    _get_project_for_user(db, project_id, current_user.id)
    task = _get_task_or_404(db, project_id, task_id)

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        _validate_status_transition(task.status, payload.status.value)
        task.status = payload.status.value

    if "assigned_to" in payload.model_fields_set:
        if payload.assigned_to is not None and db.get(User, payload.assigned_to) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
        task.assigned_to = payload.assigned_to

    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}")
def delete_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    _get_project_for_user(db, project_id, current_user.id)
    task = _get_task_or_404(db, project_id, task_id)
    task.is_deleted = True
    db.commit()
    return {"message": "Task deleted"}
