from sqlmodel import SQLModel, Field, create_engine, select, Session
from sqlalchemy import Column, String, TIMESTAMP, Boolean, Text, func, Date, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from typing import Optional
from models import UserCreate, UserCreateResponse, UserUpdate, UserStatsResponse
from datetime import datetime, date
from security import get_password_hash
import os
from fastapi import HTTPException
import uuid

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,
                        pool_size=5,
                        max_overflow=10,
                        echo=False, )


# Define the User model for the database
class UserCreateDB(SQLModel, table=True):
    
    __tablename__ = "users"
    
    user_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, unique=True)
    )
    
    username: str = Field(sa_column=Column(String(50), nullable=False, unique=True))
    hashed_password: str = Field(sa_column=Column(String(255), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    full_name: Optional[str] = Field(default=None, sa_column=Column(String(255), nullable=True))
    bio: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    avatar_url: Optional[str] = Field(default=None, sa_column=Column(String(500), nullable=True))
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False))
    active: bool = Field(sa_column=Column(Boolean, nullable=False, default=True, server_default="true"))
    
    
    
# Define the Follows_table
class follows_table(SQLModel, table=True):
    
    __tablename__ = "follows"
    
    follower_id: uuid.UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False))
    followee_id: uuid.UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, nullable=False))
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))


# Define the Reading Streaks table
class reading_streaks_table(SQLModel, table=True):
    
    __tablename__ = "reading_streaks"
    
    user_id: uuid.UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, nullable=False))
    current_streak: int = Field(default=0, sa_column=Column())
    longest_streak: int = Field(default=0, sa_column=Column())
    last_read_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    updated_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))


#Define the Notifications table
class notifications_table(SQLModel, table=True):
    
    __tablename__ = "notifications"
    
    notification_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True, unique=True)
    )
    recipient_id: uuid.UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), nullable=False))
    actor_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), nullable=True))
    
    type: str = Field(sa_column=Column(String(50), nullable=False))
    
    reference_id: Optional[uuid.UUID] = Field(default=None, sa_column=Column(PG_UUID(as_uuid=True), nullable=True))
    read: bool = Field(sa_column=Column(Boolean, nullable=False, default=False, server_default="false"))
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))
    
    

def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized and tables created (if not exist).")


def close_db_connection():
    engine.dispose()
    print("Database connection closed.")
    
    
def create_user(session: Session, user: UserCreate) -> UserCreateResponse:
    created = str(datetime.now().isoformat())
    user_id = str(uuid.uuid1())
    password_hash = get_password_hash(user.password)
    bio = user.bio if user.bio else None
    avatar_url = user.avatar_url if user.avatar_url else None
    
    user = UserCreateDB(user_id=user_id, username=user.username, hashed_password=password_hash, email=user.email, full_name=user.full_name, bio=bio, avatar_url=avatar_url, created_at=created)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    response = UserCreateResponse({
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "created_at": created,
        "updated_at": created,
        "active": True
    })
    
    return response
    
    
def get_user_info(session: Session, user_id: str) -> UserCreateResponse:
    user = session.get(UserCreateDB, user_id)
    
    if (not user):
        raise HTTPException(status_code=404, detail=f"User {user_id} does not exists!")
    else: 
        response = UserCreateResponse({
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "active": user.active
        })
        
        return response
    
    

    
def get_username_by_id(session: Session, user_id: str) -> str:
    user = session.get(UserCreateDB, user_id)
    
    if (not user):
        raise HTTPException(status_code=404, detail=f"User {user_id} does not exists!")
    else: 
        return user.username
    

def get_user_by_username(session: Session, username: str) -> UserCreateResponse:
    query = select(UserCreateDB).where(UserCreateDB.username == username)
    result = session.exec(query).first()
    
    if (not result):
        raise HTTPException(status_code=404, detail=f"The user with username: {username} does not exists!")
    else:
        return result  

 
def edit_user_info(session: Session, original_user: UserCreateResponse, update: UserUpdate) -> UserCreateResponse:
    
    # Use Pydantic's model_dump with exclude_unset to get only the fields that were provided in the update
    updated_info = update.model_dump(exclude_unset=True)
    
    #Verify if user exists
    if not original_user:
        raise HTTPException(status_code=404, detail=f"User {original_user.user_id} does not exist!")
    
    # If the password is being updated, hash the new password before saving
    if update.password:
        updated_info["hashed_password"] = get_password_hash(update.password)
        del updated_info["password"]
    
    #Update only the fields that were provided in the update request
    for field, value in updated_info.items():
        setattr(original_user, field, value)
        
    original_user.updated_at = datetime.now()
        
    session.add(original_user)
    session.commit()
    session.refresh(original_user)
    

    return original_user


def update_follower(session: Session, follower_id: str, followee_id: str):
    
    #Verify both users exist
    follower = session.get(UserCreateDB, follower_id)
    followee = session.get(UserCreateDB, followee_id)
    
    if not follower and not followee:
        raise HTTPException(status_code=404, detail=f"Both users do not exist! Follower: {follower_id}, Followee: {followee_id}")
    elif not followee:
        raise HTTPException(status_code=404, detail=f"Followee user {followee_id} does not exist!")
    elif not follower:
        raise HTTPException(status_code=404, detail=f"Follower user {follower_id} does not exist!")
    
    
    
    #Verify the follow relationship does not already exist
    existing_follow = session.get(follows_table, (follower_id, followee_id))
    
    if existing_follow:
        raise HTTPException(status_code=400, detail=f"User {follower_id} is already following {followee_id}!")
    
    
    #Create new follow relationship
    new_follow = follows_table(follower_id=follower_id, followee_id=followee_id)

    session.add(new_follow)
    
    #Update the updated_at timestamp for both users
    follower.updated_at = datetime.now()
    followee.updated_at = datetime.now()
    
    session.commit()
    session.refresh(new_follow)
    
    return new_follow
    


def remove_followers(session: Session, unfollower: str, unfollowing: str):
    follow = session.get(follows_table, (unfollower, unfollowing))
    
    if not follow:
        raise HTTPException(status_code=404, detail=f"Follow relationship between {unfollower} and {unfollowing} does not exist!")
    
    session.delete(follow)
    session.commit()
    
    return {"follower_id": unfollower, "followee_id": unfollowing, "status": "unfollowed"}


def delete_user(session: Session, user_id: str):
    user = session.get(UserCreateDB, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
    
    session.delete(user)
    session.commit()
    

def most_active_users(session: Session) -> list[UserStatsResponse]:
    
    query = text("""
        SELECT
            user_id,
            username,
            followers,
            following,
            posts,
            comments
        FROM user_stats
        ORDER BY (followers + posts + comments) DESC
        LIMIT 10)
    """)
    
    results = session.exec(query).mappings().all()
    
    return [UserStatsResponse(**result) for result in results]
    


def most_followed_users(session: Session) -> list[UserStatsResponse]:
    query = text("""
        SELECT
            user_id,
            username,
            followers,
            following,
            posts,
            comments
        FROM user_stats
        ORDER BY followers DESC
        LIMIT 10
    """)
    
    results = session.exec(query).mappings().all()
    
    return [UserStatsResponse(**result) for result in results]
    