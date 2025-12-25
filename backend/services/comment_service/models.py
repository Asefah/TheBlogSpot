from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    user_id: str
    post_id: str
    username: str = Field(..., min_length=3, max_length=50)
    content: str = Field(..., min_length=1, max_length=500)
    likes: int = 0
    dislikes: int = 0
    
class CommentResponse(BaseModel):
    user_id: str
    post_id: str
    username: str
    comment_id: str
    content: str = Field(..., min_length=1, max_length=500)
    likes: int
    dislikes: int
    edited_at: str

class CommentEdit(BaseModel):
    content: Optional[str] = Field(..., min_length=1, max_length=500)