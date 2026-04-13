from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schemas.project import ProjectRole
from app.schemas.task import TaskAssignRequest, TaskCreate, TaskResponse, TaskStatus, TaskUpdate
from app.services.dependencies import get_current_user


router = APIRouter(prefix="/api/projects/{project_id}/tasks", tags=["tasks"])


def _get_project_role_for_user(db: Session, project_id: int, user_id: int) -> tuple[Project, ProjectRole]:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.is_deleted.is_(False),
        )
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.owner_id == user_id:
        return project, ProjectRole.OWNER

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project, ProjectRole(member.role)


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


def _assert_can_create_task(role: ProjectRole) -> None:
    if role not in {ProjectRole.OWNER, ProjectRole.MEMBER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role to create tasks")


def _assert_can_assign_task(role: ProjectRole) -> None:
    if role != ProjectRole.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can assign tasks")


def _assert_can_edit_task(role: ProjectRole, task: Task, current_user_id: int) -> None:
    if role == ProjectRole.OWNER:
        return
    if task.assigned_to == current_user_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner or assigned user can edit task")


def _assert_assign_target_is_project_member(db: Session, project: Project, user_id: int) -> None:
    if project.owner_id == user_id:
        return
    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == user_id,
        )
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user is not a project member")


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
    project, role = _get_project_role_for_user(db, project_id, current_user.id)
    _assert_can_create_task(role)

    if payload.assigned_to is not None and db.get(User, payload.assigned_to) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
    if payload.assigned_to is not None:
        _assert_assign_target_is_project_member(db, project, payload.assigned_to)

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
    _get_project_role_for_user(db, project_id, current_user.id)
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
    _get_project_role_for_user(db, project_id, current_user.id)
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
    project, role = _get_project_role_for_user(db, project_id, current_user.id)
    task = _get_task_or_404(db, project_id, task_id)
    _assert_can_edit_task(role, task, current_user.id)

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.status is not None:
        _validate_status_transition(task.status, payload.status.value)
        task.status = payload.status.value

    if "assigned_to" in payload.model_fields_set:
        _assert_can_assign_task(role)
        if payload.assigned_to is not None:
            if db.get(User, payload.assigned_to) is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
            _assert_assign_target_is_project_member(db, project, payload.assigned_to)
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
    _, role = _get_project_role_for_user(db, project_id, current_user.id)
    if role != ProjectRole.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can delete tasks")
    task = _get_task_or_404(db, project_id, task_id)
    task.is_deleted = True
    db.commit()
    return {"message": "Task deleted"}


@router.put("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    project_id: int,
    task_id: int,
    payload: TaskAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    project, role = _get_project_role_for_user(db, project_id, current_user.id)
    _assert_can_assign_task(role)
    task = _get_task_or_404(db, project_id, task_id)

    target_user = db.get(User, payload.assigned_to)
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

    _assert_assign_target_is_project_member(db, project, payload.assigned_to)
    task.assigned_to = payload.assigned_to
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)
