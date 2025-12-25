from fastapi import FastAPI, HTTPException
from datetime import datetime
from models import PostCreate, PostResponse, PostEdit, PostSummary
from db import init_db, close_db_connection, engine, create_new_post, retrieve_post, retrieve_post_summary, retrieve_user_posts, edit_post_info, add_like, add_dislike
import httpx
import logging
from contextlib import asynccontextmanager, contextmanager
from sqlmodel import Session
import os

USER_SERVICE_BASE = os.getenv("USER_SERVICE_BASE", "http://user-service:8000")
COMMENT_SERVICE_BASE = os.getenv("COMMENT_SERVICE_BASE", "http://comment-service:8002")


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
    title="Post Service",
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
            "service": "Post Service",
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
        
        
@app.post("/posts", status_code=201, response_model=PostResponse)
async def create_post(post: PostCreate):
    
    user_req = f"{USER_SERVICE_BASE}/users/{post.user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        raise HTTPException(status_code=404, detail= f"User {post.user_id} not found!")
    
    with get_session() as session:
        new_post = create_new_post(session, post)
        
        logger.info(f"Post {new_post['post_id']} created by user {post.user_id}")
        return new_post
    

@app.get("/posts/{post_id}", status_code=201 ,response_model=PostResponse)
async def get_post(post_id: str):
    
    with get_session() as session:
        post = retrieve_post(session, post_id)
        
        logger.info(f"Retrieved post {post_id}")
        return post


@app.get("/posts/{post_id}/summary", status_code=201, response_model=PostSummary)
async def get_post_summary(post_id: str):
    
    with get_session() as session:
        summary = retrieve_post_summary(session, post_id)
        
        logger.info(f"Retrieved summary for post {post_id}")
        return summary
    

@app.get("/users/{user_id}/posts", status_code=200)
async def get_user_post_summary(user_id: str):
    
    user_req = f"{USER_SERVICE_BASE}/users/{user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        raise HTTPException(status_code=404, detail= f"User {user_id} not found!")
    
    with get_session() as session:
        posts = retrieve_user_posts(session, user_id)
        logger.info(f"Retrieved posts for user {user_id}")
        return posts
        

@app.put("posts/{user_id}/{post_id}", status_code=200)
async def edit_post(user_id: str, post_id: str, edit: PostEdit):
    
    user_req = f"{USER_SERVICE_BASE}/users/{user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        raise HTTPException(status_code=404, detail= f"User {user_id} not found!")
    
    with get_session() as session:
        updated_post = edit_post_info(session, user_id, post_id, edit)
        
        logger.info(f"Post {post_id} edited by user {user_id}")
        return updated_post
    

@app.delete("/posts/delete/{user_id}/{post_id}", status_code=204)
async def delete_post(user_id: str, post_id: str):
    
    user_req = f"{USER_SERVICE_BASE}/users/{user_id}"
    user = httpx.get(user_req)
    
    if not user.status_code == 200:
        logger.warning(f"User {user_id} not found when trying to delete post {post_id}")
        raise HTTPException(status_code=404, detail= f"User {user_id} not found!")
    
    with get_session() as session:
        post = retrieve_post(session, post_id)
        
        if post.user_id != user_id:
            logger.warning(f"User {user_id} unauthorized to delete post {post_id}")
            raise HTTPException(status_code=403, detail="User not authorized to delete this post!")
        
        session.delete(post)
        session.commit()
    
    
        #delete comments associated with post
        post_req = f"{COMMENT_SERVICE_BASE}/posts/{post_id}/comments"
        comments = httpx.get(post_req)
        
        if comments.status_code == 200:
            for comment in comments.json():
                delete_req = f"{COMMENT_SERVICE_BASE}/comments/delete/{user_id}/{comment['comment_id']}"
                httpx.delete(delete_req)
        
        logger.info(f"Post {post_id} deleted by user {user_id}")
        return {"detail": "Post deleted successfully"}



@app.put("/posts/{post_id}/like", status_code=200)
async def like_post(post_id: str):
    
    with get_session() as session:
        updated_post = add_like(session, post_id)
        
        #logging
        logger.info(f"Post {post_id} liked!")
        return updated_post
        

@app.put("/posts/{post_id}/dislike", status_code=200)
async def dislike_post(post_id: str):
    
    with get_session() as session:
        post = retrieve_post(session, post_id)
        updated_post = add_dislike(session, post)
        
        logger.info(f"Post {post_id} disliked!")
        return updated_post