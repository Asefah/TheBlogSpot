# Project Title and Description
## - Title: Ama's Blog Spot
## - Description: A blog community with three main services:
    - User Service: Users can create a profile using username, email, password, and an optional full name. Each user is assigned a unique user_id. The user service will be contacted by both the post service and the commenting service to check if the user exists before any activity can be done.

    - Post Service: Users who have a user profile saved will be able to make a blog post where they will need their user_id assigned by the user service in order to post. Each post will be assigned a unique post_id. Users with a specific post id can retrieve posts using that id and they can also edit the post using that post_id and their user_id. If their user_id does not match the user_id of the original poster, they will not be able to edit the post. 

    - Comment Service: Users can comment on a specific post using it's post_id and their user_id. Each comment is assigned a unique comment_id. Using this comment_id, users can retrieve specific comments and like or dislike it.
## - Prerequisites
    - Python 3.12
    - Dockerfile
    - Docker Compose
    - Redis
    - Nginx
    - Curl (use "apt-get update && apt-get install -y curl" in the terminal)
## - Installation + Setup
    - Step 1: Download Folder
    - Step 2: Make sure prerequisites are installed
    - Step 3: From root of folder, run "docker compose up"
## - Usage Instructions
    - To check health of user_service: run in another terminal "curl http://localhost:8000/health"
    - To check health of post_service: run in another terminal "curl http://localhost:8001/health"
    - To check health of comment_service: run in another terminal "curl http://localhost:8002/health"
## - API Documentation
### Health Endpoints:
    - user-service:
        - Request Example: "http://localhost:8000/health
        - Response Example: {
            "service": "User Service",
            "status": "healthy",
        }

    - post-service:
        - Request Example: "http://localhost:8001/health"
        - Response Example: {
            "service": "Post Service",
            "status": "healthy",
            "dependencies": {
                "User Service": {
                    "status": "healthy",
                    "response_time_ms": 6.1739999999999995
                }
            }
        }

    - comment-service:
        - Request Example: "http://localhost:8002/health"
        - Response Example: {
            "service": "Post Service",
            "status": "healthy",
            "dependencies": {
                "User Service": {
                    "status": "healthy",
                    "response_time_ms": 5.066
                }
            }
        }

## - Testing
    - After setting up the the system (using docker-compose up), run the health endpoints in another terminal to test if the correct response is returned.

## - Project Structure
    Milestone1/
    ├── README.md
    ├── CODE_PROVENANCE.md
    ├── architecture-diagram.png
    ├── docker-compose.yml
    ├── comment-service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── main.py
    │   └── models.py
    ├── post-service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── main.py
    │   └── models.py
    └── user-service/
        ├── Dockerfile
        ├── requirements.txt
        ├── main.py
        └── models.py

