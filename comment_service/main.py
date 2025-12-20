from fastapi import FastAPI, HTTPException
from models import CommentCreate, CommentResponse, CommentEdit
import httpx
import os
import logging
from contextlib import asynccontextmanager, contextmanager
from sqlmodel import Session
from db import init_db, close_db_connection, engine, create_new_comment, retrieve_comment, retrieve_user_comments, retrieve_post_comments, edit_comment_info, add_like, add_dislike

USER_SERVICE_BASE = os.getenv("USER_SERVICE_BASE", "http://user-service:8000")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    close_db_connection()
    
    
@contextmanager    
def get_session():
    try:
        with Session(engine) as session:
            yield session
    finally:
        session.close()
        
        
#LOGGING SETUP
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./logs/cache_log.txt", mode="a"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
   

app = FastAPI(
    title="Comment Service",
    lifespan=lifespan
)

#endpoints
@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{USER_SERVICE_BASE}/health")
        if resp.status_code != 200:
            return {
                "status": "unhealthy",
                "details": "User Service returned non-200",
                "code": resp.status_code
            }
        return {
            "service": "Comment Service",
            "status": "healthy",
            "dependencies": {
                "User Service": {
                    "status": "healthy",
                    "response_time_ms": resp.elapsed.total_seconds() * 1000
                }
            }
        }
    except Exception as e:
        return {
            "status": "starting",
            "details": f"User Service not reachable: {str(e)}"
        }
       
    
@app.post("/comments", status_code=201, response_model=CommentResponse)
async def create_comment(comment:CommentCreate):
    
    user_req = f"{USER_SERVICE_BASE}/users/{comment.user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        raise HTTPException(status_code=404, detail= f"User {comment.user_id} not found!")
    
    with get_session() as session:
        new_comment = create_new_comment(session, comment)

        logger.info(f"Post {new_comment['comment_id']} created by user {comment.user_id}")
        
        return CommentResponse({
            "comment_id": new_comment.comment_id,
            "user_id": new_comment.user_id,
            "post_id": new_comment.post_id,
            "username": new_comment.username,
            "content": new_comment.content,
            "likes": new_comment.likes,
            "dislikes": new_comment.dislikes,
            "edited_at": new_comment.edited_at
        })
    
    
    
@app.get("/comments/{comment_id}")
async def get_comment(comment_id: str):
    
    with get_session() as session:
        comment = retrieve_comment(session, comment_id)
        
        logger.info(f"Retrieved comment {comment_id}")
        return comment
   
    

@app.get("/users/{user_id}/comments", status_code=200)
async def get_user_comments(user_id: str):

    with get_session() as session:
        comments = retrieve_user_comments(session, user_id)
        
        logger.info(f"Retrieved comments for user {user_id}")
        return comments
    
   
    
@app.get("/posts/{post_id}/comments", status_code=200)
async def get_post_comments(post_id: str):
    
    with get_session() as session:
        comments = retrieve_post_comments(session, post_id)
        
        logger.info(f"Retrieved comments for post {post_id}!")
        return comments



@app.put("/comments/{user_id}/{comment_id}", response_model=CommentResponse)
async def edit_comment(user_id: str, comment_id: str, comment_edit: CommentEdit):
    
    user_req = f"{USER_SERVICE_BASE}/users/{user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        raise HTTPException(status_code=404, detail= f"User {user_id} not found!")
    
    with get_session() as session:
        comment = retrieve_comment(session, comment_id)
        
        if comment.user_id != user_id:
            raise HTTPException(status_code=403, detail="User not authorized to edit this comment!")
        
        edited_comment = edit_comment_info(session, comment, comment_edit)
        
        logger.info(f"Comment {comment_id} edited by user {user_id}!")
        return edited_comment
    
    

@app.delete("/comments/delete/{user_id}/{comment_id}", status_code=204)
async def delete_comment(comment_id: str, user_id: str):
    
    user_req = f"{USER_SERVICE_BASE}/users/{user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        logger.warning(f"User {user_id} not found when trying to delete comment {comment_id}")
        raise HTTPException(status_code=404, detail= f"User {user_id} not found!")
    
    with get_session() as session:
        comment = retrieve_comment(session, comment_id)
        
        if comment.user_id != user_id:
            logger.warning(f"User {user_id} unauthorized to delete comment {comment_id}")
            raise HTTPException(status_code=403, detail="User not authorized to delete the post!")
        
        session.delete(comment)
        session.commit()
        
        logger.info(f"Comment {comment_id} deleted by user {user_id}!")
        
    return {"detail": "Comment deleted successfully!"}



@app.put("/comments/{comment_id}/like", status_code=200)
async def like_comment(comment_id: str):
    
    with get_session() as session:
        liked_comment = add_like(session, comment_id)
        
        #logging
        logger.info(f"Comment {comment_id} liked!")
        return liked_comment



@app.put("/comments/{comment_id}/dislike", status_code=200)
async def dislike_comment(comment_id: str):
    
    with get_session() as session:
        disliked_comment = add_dislike(session, comment_id)
        
        #logging
        logger.info(f"Comment {comment_id} disliked!")
        return disliked_comment