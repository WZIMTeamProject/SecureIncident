from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommentResponse(BaseModel):
    id: UUID
    author_id: UUID
    author_username: str | None = None
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
