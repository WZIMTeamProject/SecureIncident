from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CommentResponse(BaseModel):
    id: UUID
    author_id: UUID
    author_username: Optional[str] = None
    content: str
    created_at: datetime


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
