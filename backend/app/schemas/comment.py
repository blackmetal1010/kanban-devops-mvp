from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class CommentUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    author_id: int
    text: str
    created_at: datetime
    updated_at: datetime
