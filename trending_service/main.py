from fastapi import FastAPI, HTTPException
from models import trendingCommentResponse, trendingPostResponse, trendingUsers
import httpx
import os
import logging
from contextlib import contextmanager
from sqlmodel import Session
from ..user_service import db as user_db
from ..post_service import db as post_db
from ..comment_service import db as comment_db

USER_SERVICE_BASE = os.getenv("USER_SERVICE_BASE", "http://user_service:8000")
POST_SERVICE_BASE = os.getenv("POST_SERVICE_BASE", "http://post_service:8001")
COMMENT_SERVICE_BASE = os.getenv("COMMENT_SERVICE_BASE", "http://comment_service:8002")

comment_engine = comment_db.engine
post_engine = post_db.engine
user_engine = user_db.engine
    

@contextmanager    
def get_session(engine):
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
    title="Comment Service"
)

#endpoints
@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            user_resp = await client.get(f"{USER_SERVICE_BASE}/health")
        if user_resp.status_code != 200:
            return {
                "status": "unhealthy",
                "details": "User Service returned non-200",
                "code": user_resp.status_code
            }
            
        async with httpx.AsyncClient(timeout=2.0) as client:
            post_resp = await client.get(f"{POST_SERVICE_BASE}/health")
            
        if post_resp.status_code != 200:
            return {
                "status": "unhealthy",
                "details": "Post Service returned non-200",
                "code": post_resp.status_code
            }
            
        async with httpx.AsyncClient(timeout=2.0) as client:
            comment_resp = await client.get(f"{COMMENT_SERVICE_BASE}/health")
            
        if comment_resp.status_code != 200:
            return {
                "status": "unhealthy",
                "details": "Comment Service returned non-200",
                "code": comment_resp.status_code
            }
            
        return {
            "service": "Comment Service",
            "status": "healthy",
            "dependencies": {
                "User Service": {
                    "status": "healthy",
                    "response_time_ms": user_resp.elapsed.total_seconds() * 1000
                }, 
                    "Post Service": {
                    "status": "healthy",
                    "response_time_ms": post_resp.elapsed.total_seconds() * 1000
                },
                "Comment Service": {
                    "status": "healthy",
                    "response_time_ms": comment_resp.elapsed.total_seconds() * 1000
                },
            }
        }
    except Exception as e:
        return {
            "status": "starting",
            "details": f"Trending Service not reachable: {str(e)}"
        }
        
        
        
        
@app.get("/trending/posts", status_code=200)
async def get_trending_posts():
    
    with get_session(post_engine) as post_session:
        trending_posts = post_db.get_trending_posts(post_session)
        
        posts_list = []
        
        for post in trending_posts:
            posts_list.append(trendingPostResponse(
                post_id=post.post_id,
                title=post.title,
                category=post.category,
                likes=post.likes,
                dislikes=post.dislikes,
                edited_at=post.edited_at
            ))
            
        
        return posts_list
    
    
@app.get("/trending/posts/likes", status_code=200)
async def get_trending_posts_by_likes():
    
    with get_session(post_engine) as post_session:
        liked_posts = post_db.get_most_liked(post_session)
        
        posts_list = []
        
        for post in liked_posts:
            posts_list.append(trendingPostResponse(
                post_id=post.post_id,
                title=post.title,
                category=post.category,
                likes=post.likes,
                dislikes=post.dislikes,
                edited_at=post.edited_at
            ))
        
        return posts_list
    

@app.get("/trending/posts/dislikes", status_code=200)
async def get_trending_posts_by_dislikes():
    
    with get_session(post_engine) as post_session:
        disliked_posts = post_db.get_most_disliked(post_session)
        
        posts_list = []
        
        for post in disliked_posts:
            posts_list.append(trendingPostResponse(
                post_id=post.post_id,
                title=post.title,
                category=post.category,
                likes=post.likes,
                dislikes=post.dislikes,
                edited_at=post.edited_at
            ))
        
        return posts_list
    
    
@app.get("/trending/comments", status_code=200)
async def get_trending_comments():
    
    with get_session(comment_engine) as comment_session:
        trending_comments = comment_db.get_trending_comments(comment_session)
        
        comment_list = []
        
        for comment in trending_comments:
            comment_list.append(trendingCommentResponse(
                comment_id=comment.comment_id,
                content=comment.content,
                likes=comment.likes,
                dislikes=comment.dislikes,
                edited_at=comment.edited_at
            ))
            
        return comment_list
    

@app.get("/trending/comments/likes", status_code=200)
async def get_trending_comments_likes():
    
    with get_session(comment_engine) as comment_session:
        liked_comments = comment_db.get_most_liked_comments(comment_session)
        
        comment_list = []
        
        for comment in liked_comments:
            comment_list.append(trendingCommentResponse(
                comment_id=comment.comment_id,
                content=comment.content,
                likes=comment.likes,
                dislikes=comment.dislikes,
                edited_at=comment.edited_at
            ))
            
        return comment_list
    

@app.get("/trending/comments/dislikes", status_code=200)
async def get_trending_comments_dislikes():
    
    with get_session(comment_engine) as comment_session:
        disliked_comments = comment_db.get_most_disliked_comments(comment_session)
        
        
        comment_list = []
        
        for comment in disliked_comments:
            comment_list.append(trendingCommentResponse(
                comment_id=comment.comment_id,
                content=comment.content,
                likes=comment.likes,
                dislikes=comment.dislikes,
                edited_at=comment.edited_at
            ))
            
        return comment_list
    
    
@app.get("/trending/users/activity", status_code=200)
async def get_trending_users():
    
    with get_session(user_engine) as user_session:
        trending_users = user_db.most_active_users(user_session)
        
        users_list = []
        
        for user in trending_users:
            users_list.append(trendingUsers(
                user_id=user.user_id,
                username=user.username,
                total_likes=user.total_likes,
                total_dislikes=user.total_dislikes
            ))
            
        return users_list


@app.get("/trending/users/followers", status_code=200)
async def get_trending_user_followers():
    
    with get_session(user_engine) as user_session:
        trending_users = user_db.most_followed_users(user_session)
        
        users_list = []
        
        for user in trending_users:
            users_list.append(trendingUsers(
                user_id=user.user_id,
                username=user.username,
                total_likes=user.total_likes,
                total_dislikes=user.total_dislikes
            ))
            
        return users_list
