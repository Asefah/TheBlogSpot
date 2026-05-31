from fastapi import FastAPI
from app.api.routes.auth import router as auth_router
from app.api.routes.posts import router as posts_router
from app.api.routes.comments import router as comments_router

app = FastAPI(title="Gateway Service")

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(comments_router)

app.get("/health")
async def health_check():
    return {
        "service": "Gateway Service",
        "status": "healthy",
    }