import httpx
from jose import jwt


GATEWAY_URL = "http://localhost:8080"
USER_SERVICE_URL = "http://localhost:8000"

SECRET_KEY = "gateway_secret_key"
ALGORITHM = "HS256"


def test_signup_login_and_auth_flow():
    
    sign_up_payload = {
        "username": "ama_wuz_here",
        "email": "ama@example.com",
        "full_name": "Ama Sample",
        "password": "peterpiper123"
    }
    
    signup_response = httpx.post(
        f"{USER_SERVICE_URL}/users",
        json=sign_up_payload,
        timeout=5.0
    )
    
    assert signup_response.status_code == 201
    user_id = signup_response.json()["user_id"]
    
    
    login_payload = {
        "username": "ama_wuz_here",
        "password": "peterpiper123"
    }
    
    login_response = httpx.post(
        f"{GATEWAY_URL}/auth/login",
        json=login_payload,
        timeout=5.0
    )
    
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    assert token is not None
    
    decoded = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    
    assert decoded["sub"] == user_id
    
    
    protected_response = httpx.post(
        f"{GATEWAY_URL}/posts",
        json={"title": "Introduction Post", "content": "This is my first post."},
        headers={"Authorization": f"Bearer {token}"},
        timeout=5.0
    )
    
    assert protected_response.status_code in (200, 201)