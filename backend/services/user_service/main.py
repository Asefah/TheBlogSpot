from fastapi import FastAPI, HTTPException
from datetime import datetime
from models import UserCreate, UserCreateResponse, UserUpdate, UserLogin
from security import verify_password, get_password_hash
from db import init_db, close_db_connection, engine, create_user, edit_user_info, get_user_info, get_user_by_username, add_followers, remove_followers
from contextlib import asynccontextmanager, contextmanager
from sqlmodel import Session
import logging
import httpx
import os
import socket

HOSTNAME = socket.gethostname()



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
    title="User Service",
    lifespan=lifespan
)


#endpoints

@app.get("/")
async def root():
    return {
        "message": "Hello from User Service!",
        "instance": HOSTNAME,
        "container_id": os.getenv("HOSTNAME", "unknown")
    }
    
    
@app.get("/health")
async def health_check():
    return {
        "service": "User Service",
        "status": "healthy",
    }


@app.post("/auth/verify")
def verify_user_credentials(credentials: UserLogin):
    
    with get_session() as session:
        user = get_user_by_username(session, username=credentials.username)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "active": user.active
        }

@app.post("/users", status_code=201, response_model=UserCreateResponse)
def create_new_user(user: UserCreate):
    
    with get_session() as session:
        response = create_user(session, user)
        return response



@app.get("/users/{user_id}", status_code=200, response_model=UserCreateResponse)
def get_user(user_id: str):
    
    with get_session() as session:
        user = get_user_info(session=session, user_id=user_id)
        
        return {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "created_at": str(user.created_at),
            "followers": user.followers,
            "posts": user.posts,
            "comments": user.comments,
            "active": user.active
        }
    

@app.put("/users/{user_id}", status_code=200, response_model=UserCreateResponse)
def update_user_info(user_id: str, user_update: UserUpdate):
    
    with get_session() as session:
        original = get_user_info(session=session, user_id=user_id)
        updated_user = edit_user_info(session=session, original_user=original, update=user_update)
        
        return UserCreateResponse({
            "user_id": str(updated_user.user_id),
            "username": updated_user.username,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "created_at": str(updated_user.created_at),
            "followers": updated_user.followers,
            "posts": updated_user.posts,
            "comments": updated_user.comments,
            "active": updated_user.active
        })
        
        

@app.put("/users/follow/{user_id}", response_model=UserCreateResponse)
async def add_follower(user_id: str):
    
    with get_session() as session:
        updated_user = add_followers(session=session, user_id=user_id)
        
        return {
            "user_id": str(updated_user.user_id),
            "username": updated_user.username,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "created_at": str(updated_user.created_at),
            "followers": updated_user.followers,
            "posts": updated_user.posts,
            "comments": updated_user.comments,
            "active": updated_user.active
        }
        
@app.put("/users/unfollow/{user_id}", response_model=UserCreateResponse)
async def remove_follower(user_id: str):
    
    with get_session() as session:
        updated_user = remove_followers(session=session, user_id=user_id)
        
        return {
            "user_id": str(updated_user.user_id),
            "username": updated_user.username,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "created_at": str(updated_user.created_at),
            "followers": updated_user.followers,
            "posts": updated_user.posts,
            "comments": updated_user.comments,
            "active": updated_user.active
        }
    

@app.get("/users/posts/{user_id}", response_model=UserCreateResponse)
async def get_posts(user_id: str):
    pass

@app.get("/users/comments/{user_id}", response_model=UserCreateResponse)
async def get_comments(user_id: str):
    pass

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str):
    pass