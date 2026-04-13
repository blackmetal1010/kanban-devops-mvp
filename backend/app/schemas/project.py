from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ProjectRole(str, Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    description: str | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]


class ProjectMemberUpsertRequest(BaseModel):
    user_id: int
    role: ProjectRole


class ProjectMemberResponse(BaseModel):
    project_id: int
    user_id: int
    role: ProjectRole


class ProjectStatsResponse(BaseModel):
    project_id: int
    total: int
    todo: int
    in_progress: int
    done: int
    pct_complete: float
