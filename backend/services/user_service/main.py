from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from backend.services.post_service.models import PostResponse
from models import UserCreate, UserCreateResponse, UserUpdate, UserLogin, FollowResponse
from security import verify_password
from db import init_db, close_db_connection, engine, create_user, edit_user_info, get_user_info, get_user_by_username, update_follower, remove_followers
from contextlib import asynccontextmanager, contextmanager
from sqlmodel import Session
from typing import List
import logging
import os
import socket

HOSTNAME = socket.gethostname()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Load JWT secret from Docker secret file or environment variable
SECRET_FILE = "/run/secrets/jwt_secret"
SECRET_KEY = None
if os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "r") as f:
        SECRET_KEY = f.read().strip()
else:
    SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set (env or docker secret)")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

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
        
        return (user)
    

@app.put("/users/{user_id}", status_code=200, response_model=UserCreateResponse)
def update_user_info(user_id: str, user_update: UserUpdate):
    
    with get_session() as session:
        original = get_user_info(session=session, user_id=user_id)
        
        if not original:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
        
        updated_user = edit_user_info(session=session, original_user=original, update=user_update)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
        
        
        return (updated_user)
        
        

@app.put("/users/follow/{followee_id}", response_model=FollowResponse)
async def add_follower(followee_id: str, current_user_id: str = Depends(get_current_user)):
    
    with get_session() as session:
        
        #Verify followee exists
        followee = get_user_info(session=session, user_id=followee_id)
        
        if not followee:
            raise HTTPException(status_code=404, detail=f"User {followee_id} does not exist!")
        
        #Verify follower exists (current user)
        follower = get_user_info(session=session, user_id=current_user_id)
        
        if not follower:
            raise HTTPException(status_code=404, detail=f"User {current_user_id} does not exist!")
        
        follow_record = update_follower(session=session, follower_id=current_user_id, followee_id=followee_id)
        return follow_record
        
    
        
@app.put("/users/unfollow/{followee_id}")
async def remove_follower(followee_id: str, current_user_id: str = Depends(get_current_user)):
    
    with get_session() as session:
        result = remove_followers(session=session, unfollower=current_user_id, unfollowing=followee_id)
        return result
    

@app.get("/users/posts/{user_id}", response_model=List[PostResponse])
async def get_posts(user_id: str):
    
    #TODO: Implement this endpoint to retrieve posts for a user by making a request to the Post Service
    
    # Verify user exists
    with get_session() as session:
        user = get_user_info(session=session, user_id=user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
        
    

@app.get("/users/comments/{user_id}", response_model=UserCreateResponse)
async def get_comments(user_id: str):
    
    #TODO: Implement this endpoint to retrieve comments for a user by making a request to the Comment Service
    
    # Verify user exists
    with get_session() as session:
        user = get_user_info(session=session, user_id=user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
    

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str):
    
    #TODO: Implement this endpoint to delete a user and all associated data (posts, comments, follows) by making requests to the respective services

    # Verify user exists
    with get_session() as session:
        user = get_user_info(session=session, user_id=user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
        
        # Deactivate user first by setting active to False
        user_update = UserUpdate(active=False)
        updated_user = edit_user_info(session=session, original_user=user, update=user_update)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
        
        
        # Then delete user by making a request to the User Service 
        
        
@app.post("/users/{user_id}/deactivate", status_code=200, response_model=UserCreateResponse)
def deactivate_user(user_id: str):
    
    #TODO: Implement this endpoint to deactivate a user by making a request to the User Service
    
    with get_session() as session:
        original = get_user_info(session=session, user_id=user_id)
        
        # Verify user exists
        if not original:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")
        
        #Create a UserUpdate object with active set to False to deactivate the user
        user_update = UserUpdate(active=False)
        updated_user = edit_user_info(session=session, original_user=original, update=user_update)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail=f"User {user_id} does not exist!")