from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    author_id: int
    text: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
