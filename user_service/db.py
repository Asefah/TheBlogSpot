from sqlmodel import SQLModel, Field, create_engine, select, Enum, Session
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, func
from typing import Optional
from pydantic import EmailStr
from models import UserCreate, UserCreateResponse, UserUpdate
from datetime import datetime
import os
from fastapi import HTTPException
import uuid

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,
                        pool_size=5,
                        max_overflow=10,
                        echo=False, )



class UserCreateDB(SQLModel, table=True):
    
    __tablename__ = "users"
    
    user_id: str = Field(sa_column=Column(String, primary_key=True, unique=True))
    username: str = Field(sa_column=Column(String(50), nullable=False))
    email: str = Field(sa_column=Column(String(255), unique=True, nullable=False))
    full_name: str = Field(sa_column=Column(String(255), nullable=True))
    created_at: str = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))
    followers: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    posts: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    comments: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    active: int = Field(sa_column=Column(Boolean, nullable=False, default=True, server_default="true"))
    
     
    
def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized and tables created (if not exist).")


def close_db_connection():
    engine.dispose()
    print("Database connection closed.")
    
    
def create_user(session: Session, user: UserCreate) -> UserCreateResponse:
    created = str(datetime.now().isoformat())
    user_id = str(uuid.uuid1())
    user = UserCreateDB(user_id=user_id, username=user.username, email=user.email, full_name=user.full_name, created_at=created)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    response = {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": created,
        "followers": 0,
        "posts": 0,
        "comments": 0,
        "active": True
    }
    
    return response
    
    
def get_user_info(session: Session, user_id: str) -> UserCreateResponse:
    user = session.get(UserCreateDB, user_id)
    
    if (not user):
        raise HTTPException(status_code=404, detail=f"User {user_id} does not exists!")
    else: 
        return user
    
    
def edit_user_info(session: Session, original_user: UserCreateResponse, update: UserUpdate) -> UserCreateResponse:
    updated_info = update.model_dump(exclude_unset=True)
    
    for field, value in updated_info.items():
        setattr(original_user, field, value)
        
    session.add(original_user)
    session.commit()
    session.refresh(original_user)

    return original_user


def add_followers(session: Session, user_id: str) -> UserCreateResponse:
    user = session.get(UserCreateDB, user_id)
    
    setattr(user, "followers", user.followers+1)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

def remove_followers(session: Session, user_id: str) -> UserCreateResponse:
    user = session.get(UserCreateDB, user_id)
    
    setattr(user, "followers", user.followers-1)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

def most_active_users(session: Session) -> list[UserCreateResponse]:
    query = select(UserCreateDB).order_by(UserCreateDB.posts.desc())
    results = session.exec(query).limit(10).all()
    
    return results

def most_followed_users(session: Session) -> list[UserCreateResponse]:
    query = select(UserCreateDB).order_by(UserCreateDB.followers.desc())
    results = session.exec(query).limit(10).all()
    
    return results
    