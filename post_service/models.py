from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


categoryList = Literal [
        "Lifestyle", 
        "Food", 
        "Travel", 
        "Finance", 
        "Technology", 
        "Business", 
        "Health and Fitness", 
        "Other"
    ]


class PostCreate(BaseModel):
    user_id: str
    username: str = Field(..., min_length=3, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    category: str = categoryList
    content: str = Field(..., min_length=1, max_length=5000)
    likes: int = 0
    dislikes: int = 0
    
class PostResponse(BaseModel):
    post_id: str
    user_id: str
    username: str = Field(..., min_length=3, max_length=50)
    title: str = Field(..., min_length=1, max_length=200)
    category: str = categoryList
    content: str = Field(..., min_length=1, max_length=5000)
    likes: int
    dislikes: int
    edited_at: str
    
    
class PostEdit(BaseModel):
    title: Optional[str] = Field(..., min_length=1, max_length=200)
    content: Optional[str] = Field(..., min_length=1, max_length=5000)
    
class PostSummary(BaseModel):
    post_id: str
    username: str
    title: str = Field(..., min_length=1, max_length=200)
    category: str = categoryList
    likes: int
    dislikes: int
    edited_at: str