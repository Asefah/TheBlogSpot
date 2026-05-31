# TheBlogSpot - Complete Directory Guide

## Overview
TheBlogSpot is a **microservices-based blog platform** built with **FastAPI**, **PostgreSQL**, **Redis**, **Docker**, and **Nginx**. The application is containerized and uses Docker Compose for orchestration. Users can create accounts, post blog entries, comment on posts, and engage through likes/dislikes.

---

## Architecture

### High-Level Design
```
Client (curl/Frontend) 
    ↓
Nginx (Port 80) - Reverse Proxy / Load Balancer
    ↓
API Gateway (Port 8080) - Auth & Request Routing
    ↓
├── User Service (Port 8000) + PostgreSQL + Redis
├── Post Service (Port 8001) + PostgreSQL + Redis
├── Comment Service (Port 8002) + PostgreSQL + Redis
└── Trending Service (Port 8003) - Aggregates Analytics
```

### Network Configuration
- **Network Name**: `blogspot-network` (Docker bridge)
- **Redis Cache**: Centralized in-memory cache for all services
- **Health Checks**: Each service includes lifespan management and dependency monitoring

---

## Directory Structure

### Root-Level Files
```
TheBlogSpot/
├── README.md                    # Project setup & usage instructions
├── CODE_PROVENANCE.md          # Attribution & source documentation
├── DIRECTORY_GUIDE.md          # This file
├── docker-compose.yml          # All service definitions & networking
└── architecture_diagram.png    # Visual system architecture
```

---

## Backend Directory (`/backend`)

### `/backend/docker-compose.yml`
**Purpose**: Defines all containerized services, databases, networks, and volumes.

**Key Services**:
1. **gateway**: Main entry point, handles authentication & routing (FastAPI on 8080)
2. **nginx**: Reverse proxy forwarding requests based on URL paths (80)
3. **redis**: In-memory cache shared by all services (6379)
4. **user_db, post_db, comments_db**: PostgreSQL instances for each service
5. **user_service, post_service, comment_service, trending_service**: Microservices
6. **Volume Management**: Persistent storage for PostgreSQL databases and Redis

### `/backend/nginx.conf`
**Purpose**: Nginx configuration for routing and reverse proxy setup.

**Routing Logic**:
```
/user_service/     → user_service:8000
/post_service/     → post_service:8001
/comment_service/  → comment_service:8002
/trending_service/ → trending_service:8003
/nginx-health      → Health check (returns 200)
```

Preserves headers for client IP, host forwarding, and real IP detection.

---

### `/backend/gateway` - API Gateway Service

**Technology**: FastAPI (Python 3.11)
**Port**: 8080 (maps to 8080 in docker-compose)
**Dockerfile**: Uses official Python 3.11-slim image, installs dependencies, runs Uvicorn

#### Key Files:

**`app/deps.py`**
- Dependency injection utilities
- OAuth2PasswordBearer configuration for token-based auth

**`app/core/security.py`**
- JWT token creation using PyJWT
- Secret key: `"gateway_secret_key"`
- Algorithm: `HS256`
- Token expiry: 15 minutes
- Bcrypt password hashing context

**`app/api/routes/auth.py`**
- **`POST /auth/login`**: 
  - Accepts `{username, password}`
  - Verifies credentials with User Service
  - Returns JWT access token + bearer token type
  - Sets refresh_token cookie (currently placeholder)

**`app/api/routes/posts.py`** (Currently empty - needs implementation)
- Intended for post creation, retrieval, editing

**`app/api/routes/comments.py`** (Currently empty - needs implementation)
- Intended for comment management

**`requirements.txt`**: FastAPI, Uvicorn, PyJWT, passlib, httpx, bcrypt

---

### `/backend/services` - Core Microservices

All services follow the **same pattern**:
- FastAPI framework with Uvicorn
- SQLModel for ORM
- PostgreSQL database connection
- Redis integration (comments service only)
- Health check endpoints
- Dependency health reporting

#### **1. User Service** (`/services/user_service`)

**Port**: 8000
**Database**: PostgreSQL (user_db) with `users.sql` schema
**Purpose**: User account management, authentication, follower tracking

**Key Endpoints**:
- `GET /health` - Service health with dependency status
- `POST /auth/verify` - Verify credentials (username + password)
- `POST /users` - Create new user account
- `GET /users/{user_id}` - Retrieve user profile
- `PUT /users/{user_id}` - Update user info
- `PUT /users/follow/{user_id}` - Add follower
- `PUT /users/unfollow/{user_id}` - Remove follower
- `DELETE /users/{user_id}` - Delete user account

**Database Schema** (`users.sql`):
- `users` table with fields: user_id (UUID), username, email, hashed_password, full_name, created_at, followers, posts, comments, active

**Key Files**:
- `main.py` - Entry point, defines FastAPI app
- `models.py` - Pydantic models (UserCreate, UserUpdate, UserLogin, UserCreateResponse)
- `db.py` - SQLAlchemy/SQLModel database operations, engine creation, session management
- `security.py` - Password hashing & verification functions
- `requirements.txt` - FastAPI, uvicorn, sqlmodel, psycopg2, httpx

---

#### **2. Post Service** (`/services/post_service`)

**Port**: 8001
**Database**: PostgreSQL (post_db) with `posts.sql` schema
**Purpose**: Blog post creation, retrieval, editing, and engagement (likes/dislikes)

**Dependencies**: 
- User Service (validates user_id exists)
- Comment Service (for cascade delete operations)

**Key Endpoints**:
- `GET /health` - Reports User Service dependency status
- `POST /posts` - Create post (requires valid user_id)
- `GET /posts/{post_id}` - Full post details
- `GET /posts/{post_id}/summary` - Post summary
- `GET /users/{user_id}/posts` - All posts by user
- `PUT /posts/{user_id}/{post_id}` - Edit post (authorization check)
- `DELETE /posts/delete/{user_id}/{post_id}` - Delete post (cascades comment deletion)
- `PUT /posts/{post_id}/like` - Increment likes
- `PUT /posts/{post_id}/dislike` - Increment dislikes

**Database Schema** (`posts.sql`):
- `posts` table: post_id, user_id, title, category, content, likes, dislikes, edited_at

**Key Features**:
- Authorization: Only post creator can edit/delete
- Logging: All operations logged to `logs/cache_log.txt`
- Service-to-service HTTP calls via httpx to validate posts before operations

**Key Files**:
- `main.py` - FastAPI app, all endpoints
- `models.py` - PostCreate, PostResponse, PostEdit, PostSummary
- `db.py` - CRUD operations, engine, session management
- `requirements.txt` - Same as user_service plus httpx

---

#### **3. Comment Service** (`/services/comment_service`)

**Port**: 8002
**Database**: PostgreSQL (comments_db) with `comments.sql` schema
**Purpose**: Comment management, like/dislike tracking with Redis caching

**Dependencies**:
- User Service (validates user_id)
- Redis (caches reaction state)

**Key Endpoints**:
- `GET /health` - Reports User Service dependency status
- `POST /comments` - Create comment on post
- `GET /comments/{comment_id}` - Get specific comment
- `GET /users/{user_id}/comments` - All comments by user
- `GET /posts/{post_id}/comments` - All comments on post
- `PUT /comments/{user_id}/{comment_id}` - Edit comment (authorization check)
- `DELETE /comments/delete/{user_id}/{comment_id}` - Delete comment
- `PUT /comments/{comment_id}/like` - Like with Redis caching (prevents double-likes in 1hr window)
- `PUT /comments/{comment_id}/dislike` - Dislike with Redis caching

**Database Schema** (`comments.sql`):
- `comments` table: comment_id, user_id, post_id, username, content, likes, dislikes, edited_at

**Redis Caching**:
- Key: `comment:{comment_id}:reactions:{user_id}`
- Value: 1 (liked) or -1 (disliked)
- TTL: 3600 seconds (1 hour)
- Prevents duplicate reactions within window

**Key Files**:
- `main.py` - FastAPI app with Redis integration
- `models.py` - CommentCreate, CommentResponse, CommentEdit
- `db.py` - Database operations
- `requirements.txt` - Includes redis package

---

#### **4. Trending Service** (`/services/trending_service`)

**Port**: 8003
**Purpose**: Analytics & trending content aggregation (no dedicated database)

**Approach**: 
- Connects directly to databases of other services via SQLAlchemy engines
- Imports db modules from user_service, post_service, comment_service
- Aggregates metrics across services

**Key Endpoints**:
- `GET /health` - Reports all service dependencies (User, Post, Comment)
- `GET /trending/posts` - Top trending posts
- `GET /trending/posts/likes` - Most liked posts
- `GET /trending/posts/dislikes` - Most disliked posts
- `GET /trending/comments` - Trending comments
- `GET /trending/comments/likes` - Most liked comments
- `GET /trending/comments/dislikes` - Most disliked comments
- `GET /trending/users/activity` - Most active users
- `GET /trending/users/followers` - Most followed users

**Response Models**:
- trendingPostResponse: post_id, title, category, likes, dislikes, edited_at
- trendingCommentResponse: comment_id, content, likes, dislikes, edited_at
- trendingUsers: user_id, username, total_likes, total_dislikes

**Key Files**:
- `main.py` - Aggregation endpoints
- `models.py` - Response models for trending data
- `requirements.txt` - FastAPI, uvicorn, httpx, sqlmodel

---

## Database Storage

### Volumes (in docker-compose.yml)
```yaml
volumes:
  user_data:        # PostgreSQL user_db storage
  post_data:        # PostgreSQL post_db storage
  comments_data:    # PostgreSQL comments_db storage
  redis_data:       # Redis persistence (AOF enabled)
```

### Connection Strings
```
User DB:     postgresql+psycopg2://blogspotuser-table:blogspotuserpass@user_db:5432/blogspotuser
Post DB:     postgresql+psycopg2://blogspotpost-table:blogspotpostpass@post_db:5432/blogspotpost
Comments DB: postgresql://blogspotuser-table:blogspotuserpass@comments_db:5432/blogspotcomments
```

---

## Frontend Directory (`/frontend`)

**Status**: Empty (not yet implemented)

**Expected Setup**: 
- React/Vue/Angular frontend application
- Communicates with API Gateway on port 8080
- Authentication via JWT tokens from `/auth/login`

---

## Tests Directory (`/tests`)

### `conftest.py`
- Pytest session-scoped fixture that waits for gateway to be ready
- Health check logic with 30-second timeout
- Used by all integration tests

### `Integration/test_auth_flow.py`
**Tests**: Complete signup → login → protected endpoint flow

**Test Cases**:
1. User signup via `POST /users` (User Service)
2. Login via `POST /auth/login` (Gateway Auth)
3. JWT token validation (decode & verify)
4. Protected endpoint access with Bearer token

**Expected Behavior**: User signup returns 201, login returns 200 with valid JWT

### `Integration/test_login.py`
**Tests**: Authentication edge cases

**Test Cases**:
1. `test_login_success()` - Valid credentials return JWT
2. `test_login_invalid_password()` - Wrong password returns 401
3. `test_protected_route_requires_auth()` - Missing auth token returns 401
4. `test_protected_route_with_auth()` - Valid token grants access (returns 200/201)

---

## How to Run

### Prerequisites
- Docker & Docker Compose installed
- Python 3.12 (for local development)
- Curl or Postman (for API testing)

### Startup
```bash
cd backend
docker compose up
```

### Service Verification
```bash
# Check User Service
curl http://localhost:8000/health

# Check Post Service
curl http://localhost:8001/health

# Check Comment Service
curl http://localhost:8002/health

# Check Trending Service
curl http://localhost:8003/health

# Check Gateway
curl http://localhost:8080/health
```

### Run Tests
```bash
cd tests
pytest -v Integration/
```

---

## Key Technologies

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | FastAPI | 0.104.1 |
| Server | Uvicorn | 0.24.0 |
| Database | PostgreSQL | 16-alpine |
| Cache | Redis | 7-alpine |
| Reverse Proxy | Nginx | latest |
| ORM | SQLModel | - |
| Auth | JWT (PyJWT) | - |
| Container | Docker | - |

---

## Common Development Tasks

### Add a New Endpoint
1. Define Pydantic model in `models.py`
2. Create database function in `db.py`
3. Add route in `main.py` with proper error handling
4. Add logging for debugging

### Modify Database Schema
1. Edit `.sql` file in service directory
2. Recreate database volume: `docker volume rm {volume_name}`
3. Restart containers: `docker compose up`

### Fix Service Communication
- Check environment variables in docker-compose.yml
- Ensure service name matches hostname
- Verify network connection: `docker network inspect blogspot-network`

### Debug Logs
- Stream service logs: `docker compose logs -f {service_name}`
- Check container logs: `docker logs {container_id}`
- Service logs in `./logs/cache_log.txt` (in containers)

---

## Security Notes

⚠️ **Current Implementation**:
- JWT secret key hardcoded ("gateway_secret_key") - **Not production-safe**
- Database credentials visible in docker-compose.yml
- No HTTPS/TLS enforced
- No rate limiting implemented
- No input validation/sanitization

**Before Production**:
- Use environment variables for secrets
- Implement rate limiting
- Add request validation
- Enable HTTPS
- Add CORS configuration
- Implement refresh tokens properly

---

## Future Enhancements

1. **Frontend**: React/Vue application for UI
2. **Gateway Routes**: Complete posts.py and comments.py endpoints
3. **WebSocket**: Real-time notifications
4. **Message Queue**: Async job processing (Celery + RabbitMQ)
5. **Search**: Elasticsearch integration for full-text search
6. **Video Support**: Multi-media post types
7. **Notifications**: Email/push notifications service
8. **Monitoring**: Prometheus metrics & Grafana dashboards

---

## Useful Commands

```bash
# View all containers
docker ps -a

# Stop all services
docker compose down

# Remove all volumes (careful!)
docker compose down -v

# View service logs in real-time
docker compose logs -f user_service

# Execute command in container
docker exec -it user_service bash

# Rebuild specific service
docker compose build --no-cache user_service

# Rebuild and start
docker compose up --build

# Health check all services
for port in 8000 8001 8002 8003 8080; do
  echo "Port $port:"; curl -s http://localhost:$port/health | jq .
done
```

---

## Contact & Questions

Refer to **README.md** for project overview.
Refer to **CODE_PROVENANCE.md** for attribution & source code references.

This is a comprehensive guide to onboard new developers. Good luck! 🚀
