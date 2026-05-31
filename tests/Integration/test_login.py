import httpx
from jose import jwt

GATEWAY_URL = "http://localhost:8080"
SECRET_KEY = "gateway_secret_key"
ALGORITHM = "HS256"

def test_login_success():
    payload = {
        "username": "ama_wuz_here",
        "password": "peterpan123"
    }

    res = httpx.post(
        f"{GATEWAY_URL}/auth/login",
        json=payload,
        timeout=5.0
    )

    assert res.status_code == 200

    body = res.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert res.cookies.get("refresh_token") == "fake-refresh-token"

    decoded = jwt.decode(
        body["access_token"],
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    assert decoded["sub"]
    
    
    
def test_login_invalid_password():
    res = httpx.post(
        f"{GATEWAY_URL}/auth/login",
        json={"username": "ama_wuz_here", "password": "wrong"},
        timeout=5.0
    )

    assert res.status_code == 401


def test_protected_route_requires_auth():
    res = httpx.post(
        f"{GATEWAY_URL}/posts",
        json={"title": "test", "content": "test"},
        timeout=5.0
    )

    assert res.status_code == 401


def test_protected_route_with_auth():
    login = httpx.post(
        f"{GATEWAY_URL}/auth/login",
        json={"username": "ama_wuz_here", "password": "peterpan123"},
        timeout=5.0
    )

    assert login.status_code == 200
    assert login.cookies.get("refresh_token") == "fake-refresh-token"

    token = login.json()["access_token"]

    res = httpx.post(
        f"{GATEWAY_URL}/posts",
        json={"title": "hello", "content": "world"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=5.0
    )

    assert res.status_code in (200, 201)

