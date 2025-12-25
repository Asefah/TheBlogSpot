from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Annotated, Optional

class trendingPostResponse(BaseModel):
    username: str
    title: str
    content: str = Field(..., min_length=1, max_length=5000)
    likes: int
    dislikes: int
    
class trendingCommentResponse(BaseModel):
    username: str
    content: str = Field(..., min_length=1, max_length=500)
    likes: int
    dislikes: int
    
class trendingUsers(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    followers: int