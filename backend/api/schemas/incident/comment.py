from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CommentResponse(BaseModel):
    id: UUID
    authorId: UUID
    authorUsername: Optional[str] = None
    content: str
    createdAt: datetime


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]