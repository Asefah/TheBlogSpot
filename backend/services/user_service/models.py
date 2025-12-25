from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str =  Field(..., min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreateResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    created_at: str
    followers: int
    posts: int
    comments: int
    active: bool
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] =  Field(default=None, min_length=8)
    active: Optional[bool] = Field(default=None)
    

