from fastapi import APIRouter, FastAPI, HTTPException, Response
from pydantic import BaseModel
import httpx

from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

USERS_SERVICE_URL = "http://user_service:8000"

class LoginRequest(BaseModel):
    username: str
    password: str
    

@router.post("/login")
async def login(data: LoginRequest, response: Response):
    
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{USERS_SERVICE_URL}/auth/verify", json=data.model_dump(), timeout=5.0)
        
    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user_data = res.json()
    
    if not user_data["active"]:
        raise HTTPException(status_code=403, detail="User is not active")
    
    access_token = create_access_token(user_data["user_id"])
    
    response.set_cookie(
        key="refresh_token",
        value="fake-refresh-token",
        httponly=True,
        secure=False,
        samesite="lax"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }