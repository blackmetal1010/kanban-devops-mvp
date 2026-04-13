from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.comment import Comment
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.dependencies import get_current_user


router = APIRouter(prefix="/api/projects/{project_id}/tasks/{task_id}/comments", tags=["comments"])


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


def _normalize_comment_text(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment text cannot be empty")
    if "<" in normalized or ">" in normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="HTML tags are not allowed")
    return normalized


def _get_comment_or_404(db: Session, task_id: int, comment_id: int) -> Comment:
    comment = db.scalar(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.task_id == task_id,
            Comment.is_deleted.is_(False),
        )
    )
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    project_id: int,
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    _get_project_for_user(db, project_id, current_user.id)
    _get_task_or_404(db, project_id, task_id)

    comment = Comment(
        task_id=task_id,
        author_id=current_user.id,
        text=_normalize_comment_text(payload.text),
        is_deleted=False,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentResponse.model_validate(comment)


@router.get("", response_model=list[CommentResponse])
def list_comments(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CommentResponse]:
    _get_project_for_user(db, project_id, current_user.id)
    _get_task_or_404(db, project_id, task_id)

    comments = db.scalars(
        select(Comment)
        .where(
            Comment.task_id == task_id,
            Comment.is_deleted.is_(False),
        )
        .order_by(Comment.created_at.desc())
    ).all()
    return [CommentResponse.model_validate(item) for item in comments]


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    project_id: int,
    task_id: int,
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    _get_project_for_user(db, project_id, current_user.id)
    _get_task_or_404(db, project_id, task_id)
    comment = _get_comment_or_404(db, task_id, comment_id)

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments")

    comment.text = _normalize_comment_text(payload.text)
    db.commit()
    db.refresh(comment)
    return CommentResponse.model_validate(comment)


@router.delete("/{comment_id}")
def delete_comment(
    project_id: int,
    task_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    _get_project_for_user(db, project_id, current_user.id)
    _get_task_or_404(db, project_id, task_id)
    comment = _get_comment_or_404(db, task_id, comment_id)

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comments")

    comment.is_deleted = True
    db.commit()
    return {"message": "Comment deleted"}
