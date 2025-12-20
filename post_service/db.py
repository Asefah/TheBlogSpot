from sqlmodel import SQLModel, Field, create_engine, select, Enum, Session
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Enum as SQLEnum
from typing import Optional
from pydantic import EmailStr
from models import PostCreate, PostResponse, PostEdit, PostSummary
from datetime import datetime
import os
from fastapi import HTTPException
import uuid
import enum

DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_engine(DATABASE_URL,
                        pool_size=5,
                        max_overflow=10,
                        echo=False, )


class PostCategory(str, enum.Enum):
    Lifestyle = "Lifestyle"
    Food = "Food"
    Travel = "Travel"
    Finance = "Finance"
    Technology = "Technology"
    Business = "Business"
    HealthAndFitness = "Health and Fitness"
    Other = "Other"
    

class PostCreateDB(SQLModel, table=True):
    
    __tablename__ = "posts"
    
    post_id: str = Field(sa_column=Column(String, primary_key=True, unique=True))
    user_id: str = Field(sa_column=Column(String, unique=True))
    username: str = Field(sa_column=Column(String(50), nullable=False))
    title: str = Field(sa_column=Column(String(200), nullable=False))
    category: PostCategory = Field(sa_column=Column(SQLEnum(PostCategory, name="post_category")), default="Other")
    content: str = Field(sa_column=Column(String(5000), nullable=False))
    likes: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    dislikes: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    edited_at: str = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))
    
    
def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized and tables created (if not exist).")


def close_db_connection():
    engine.dispose()
    print("Database connection closed.")
    
    
def create_new_post(session: Session, post: PostCreate) -> PostResponse:
    created = datetime.now().isoformat()
    post_id = str(uuid.uuid4())
    
    post = PostCreateDB(post_id=post_id, user_id=post.user_id, username=post.username, title=post.title, category=post.category, content=post.content, edited_at=created)
    
    session.add(post)
    session.commit()
    session.flush(post)
    
    response = {
        "post_id": post_id,
        "user_id": post.user_id,
        "username": post.username,
        "title": post.title,
        "category": post.category,
        "content": post.content,
        "likes": post.likes,
        "dislikes": post.dislikes,
        "edited_at": created
    }
    
    return response

def retrieve_post(session: Session, post_id: str) -> PostResponse:
    post = session.get(PostCreateDB, post_id)
    
    if (not post):
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        return post
    
def retrieve_post_summary(session: Session, post_id: str) -> PostSummary:
    post = session.get(PostCreateDB, post_id)
    
    if (not post):
        raise HTTPException(status_code=404, detail="Post not found")
    else:
        summary = PostSummary(
            post_id=post.post_id,
            title=post.title,
            category=post.category,
            likes=post.likes,
            dislikes=post.dislikes,
            edited_at=post.edited_at
        )
        return summary
    
def retrieve_user_posts(session: Session, user_id: str):
    query = select(PostCreateDB).where(PostCreateDB.user_id == user_id) 
    results = session.exec(query).all()
    return results


def edit_post_info(session: Session, user_id: str, post_id: str, edit: PostEdit) -> PostResponse:
    post = session.get(PostCreateDB, post_id)
    
    if (not post):
        raise HTTPException(status_code=404, detail="Post not found!")
    elif (post.user_id != user_id):
        raise HTTPException(status_code=403, detail="You are not authorized to edit this post!")
    
    updated_info = edit.model_dump(exclude_unset=True)
    
    for field, value in updated_info.items():
        setattr(post, field, value)
        
    setattr(post, "edited_at", str(datetime.now().isoformat()))
    
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

def add_like(session: Session, post_id: str) -> PostResponse:
    post = session.get(PostCreateDB, post_id)
    
    if (not post):
        raise HTTPException(status_code=404, detail="Post not found!")
    
    setattr(post, "likes", post.likes+1)
    
    session.add(post)
    session.commit()
    session.refresh(post)
    
    return post

def add_dislike(session: Session, post: str) -> PostResponse:
    
    post = session.get(PostCreateDB, post.post_id)
    if (not post):
        raise HTTPException(status_code=404, detail="Post not found!")
    
    setattr(post, "dislikes", post.dislikes+1)
    session.add(post)
    session.commit()
    session.refresh(post)
    
    return post


def get_trending_posts(session: Session) -> list[PostSummary]:
    statement = select(PostCreateDB).order_by((PostCreateDB.likes - PostCreateDB.dislikes).desc()).limit(10)
    results = session.exec(statement).all()
    
    trending_posts = []
    for post in results:
        summary = PostSummary(
            post_id=post.post_id,
            username=post.username,
            title=post.title,
            category=post.category,
            likes=post.likes,
            dislikes=post.dislikes,
            edited_at=post.edited_at
        )
        trending_posts.append(summary)
        
    return trending_posts

def get_most_disliked(session: Session) -> list[PostSummary]:
    statement = select(PostCreateDB).order_by(PostCreateDB.dislikes.desc()).limit(10)
    results = session.exec(statement).all()
    
    disliked_posts = []
    for post in results:
        summary = PostSummary(
            post_id=post.post_id,
            username=post.username,
            title=post.title,
            category=post.category,
            likes=post.likes,
            dislikes=post.dislikes,
            edited_at=post.edited_at
        )
        disliked_posts.append(summary)
        
    return disliked_posts

def get_most_liked(session: Session) -> list[PostSummary]:
    statement = select(PostCreateDB).order_by(PostCreateDB.likes.desc()).limit(10)
    results = session.exec(statement).all()
    
    liked_posts = []
    for post in results:
        summary = PostSummary(
            post_id=post.post_id,
            username=post.username,
            title=post.title,
            category=post.category,
            likes=post.likes,
            dislikes=post.dislikes,
            edited_at=post.edited_at
        )
        liked_posts.append(summary)
        
    return liked_posts