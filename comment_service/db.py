from sqlmodel import SQLModel, Field, create_engine, select, Enum, Session
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Enum as SQLEnum
from typing import Optional
from pydantic import EmailStr
from models import CommentCreate, CommentResponse, CommentEdit
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

class CommentCreateDB(SQLModel, table=True):
    
    __tablename__ = "comments"
    
    comment_id: str = Field(sa_column=Column(String, primary_key=True, unique=True))
    user_id: str = Field(sa_column=Column(String, nullable=False))
    post_id: str = Field(sa_column=Column(String, nullable=False))
    username: str = Field(sa_column=Column(String(50), nullable=False))
    content: str = Field(sa_column=Column(String(500), nullable=False))
    likes: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    dislikes: int = Field(sa_column=Column(Integer, nullable=False, default=0, server_default="0"))
    edited_at: str = Field(sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False))
    

def init_db():
    SQLModel.metadata.create_all(engine)
    print("Database initialized and tables created (if not exist).")


def close_db_connection():
    engine.dispose()
    print("Database connection closed.")
    
    
def create_new_comment(session: Session, comment: CommentCreate) -> CommentResponse:
    created = str(datetime.now().isoformat())
    comment_id = str(uuid.uuid4())
    
    db_comment = CommentCreateDB(
        comment_id=comment_id,
        user_id=comment.user_id,
        post_id=comment.post_id,
        username=comment.username,
        content=comment.content,
        likes=comment.likes,
        dislikes=comment.dislikes,
        edited_at=created
    )
    
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    
    return CommentResponse(
        comment_id=db_comment.comment_id,
        user_id=db_comment.user_id,
        post_id=db_comment.post_id,
        username=db_comment.username,
        content=db_comment.content,
        likes=db_comment.likes,
        dislikes=db_comment.dislikes,
        edited_at=db_comment.edited_at
    )
    
def retrieve_comment(session: Session, comment_id: str) -> Optional[CommentResponse]:
    comment = session.get(CommentCreateDB, comment_id)
    
    if (not comment):
        raise HTTPException(status_code=404, detail="Comment not found")
    else:
        return comment
    
def retrieve_user_comments(session: Session, user_id: str) -> list[CommentResponse]:
    statement = select(CommentCreateDB).where(CommentCreateDB.user_id == user_id)
    results = session.exec(statement).all()
    
    return results

def retrieve_post_comments(session: Session, post_id: str) -> list[CommentResponse]:
    statement = select(CommentCreateDB).where(CommentCreateDB.post_id == post_id)
    results = session.exec(statement).all()
    
    return results

def edit_comment_info(session: Session, comment: CommentCreateDB, comment_edit: CommentEdit) -> CommentResponse:
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found!")
    
    if comment_edit.content is not None:
        comment.content = comment_edit.content
        
    comment.edited_at = str(datetime.now().isoformat())
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return CommentResponse(
        comment_id=comment.comment_id,
        user_id=comment.user_id,
        post_id=comment.post_id,
        username=comment.username,
        content=comment.content,
        likes=comment.likes,
        dislikes=comment.dislikes,
        edited_at=comment.edited_at
    )
    
def add_like(session: Session, comment_id: str) -> CommentResponse:
    
    comment = session.get(CommentCreateDB, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found!")
    
    setattr(comment, "likes", comment.likes + 1)
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return comment

def add_dislike(session: Session, comment_id: str) -> CommentResponse:
    
    comment = session.get(CommentCreateDB, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found!")
    
    setattr(comment, "dislikes", comment.dislikes + 1)
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return comment


def get_trending_comments(session: Session) -> list[CommentResponse]:
    statement = select(CommentCreateDB).order_by((CommentCreateDB.likes - CommentCreateDB.dislikes).desc()).limit(10)
    results = session.exec(statement).all()
    
    trending_comments = []
    for comment in results:
        trending_comments.append(comment)
        
    return trending_comments



def get_most_disliked_comments(session: Session) -> list[CommentResponse]:
    statement = select(CommentCreateDB).order_by(CommentCreateDB.dislikes.desc()).limit(10)
    results = session.exec(statement).all()
    
    disliked_comments = []
    for comment in results:
        disliked_comments.append(comment)
        
    return disliked_comments


def get_most_liked_comments(session: Session) -> list[CommentResponse]:
    statement = select(CommentCreateDB).order_by(CommentCreateDB.likes.desc()).limit(10)
    results = session.exec(statement).all()
    
    liked_comments = []
    for comment in results:
        liked_comments.append(comment)
        
    return liked_comments


def get_top_commenters(session: Session) -> list[dict]:
    statement = select(CommentCreateDB.user_id, func.count(CommentCreateDB.comment_id).label("comment_count")).group_by(CommentCreateDB.user_id).order_by(func.count(CommentCreateDB.comment_id).desc()).limit(10)
    results = session.exec(statement).all()
    
    top_commenters = []
    for user_id, count in results:
        top_commenters.append({"user_id": user_id, "comment_count": count})
        
    return top_commenters
    
    
  