from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(default=None, max_length=500)


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreateResponse(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    password: Optional[str] = Field(default=None, min_length=8)
    active: Optional[bool] = None


class UserStatsResponse(BaseModel):
    user_id: UUID
    username: str
    followers: int
    following: int
    posts: int
    comments: int

    class Config:
        from_attributes = True


class ReadingStreakResponse(BaseModel):
    user_id: UUID
    current_streak: int
    longest_streak: int
    last_read_date: Optional[date] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    notification_id: UUID
    recipient_id: UUID
    actor_id: Optional[UUID] = None
    type: str
    reference_id: Optional[UUID] = None
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FollowResponse(BaseModel):
    follower_id: UUID
    followee_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True