import time
import httpx
import pytest

GATEWAY_URL = "http://localhost:8080"

def wait_for_service(url: str, timeout: int = 30):
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            respond = httpx.get(url)
            
            if respond.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Service {url} is not ready!")


@pytest.fixture(scope="session", autouse=True)
def wait_for_gateway():
    wait_for_service(f"{GATEWAY_URL}/health")